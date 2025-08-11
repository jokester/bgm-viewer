
# noinspection PyShadowingNames
from typing import (TypeVar, Any, Dict, Optional, Tuple, Type, Union, get_args, get_origin, List, Callable,
                    Awaitable, Literal, cast)
from esorm import ESModel
from typing_extensions import TypedDict, Annotated
from enum import Enum, IntEnum

from pydantic import BaseModel, AnyUrl
from pydantic.fields import FieldInfo

from esorm.model import _ESModelMeta, ESBaseModel

_pydantic_type_map: Dict[type, str] = {}


# stolen from esorm
def setup_mappings():
    """
    Create mappings for indices or try to extend it if there are new fields
    """

    # noinspection PyShadowingNames
    def get_field_data(pydantic_type: type[ESModel] | FieldInfo | Annotated) -> dict:
        """ Get field data from pydantic type """
        origin = get_origin(pydantic_type)
        args = get_args(pydantic_type)

        # Handle Union type, which must be a type definition from esorm.fields, because other unions not allowed
        if origin and (
                origin is Union
                or
                # UnionType is in newer Pythons, this works backwards
                getattr(origin, '__name__', None) == 'UnionType'
        ):
            # Optional may equal to Union[..., None], we don't use Optional in ES, but its child
            if type(None) in args:
                return get_field_data(args[0])

            for arg in args:
                if hasattr(arg, '__es_type__'):
                    result = {'type': arg.__es_type__}

                    # Handle dense_vector specific parameters
                    if arg.__es_type__ == 'dense_vector':
                        field_info = next((f for f in pydantic_type.model_fields.values()
                                           if f.annotation == pydantic_type), None)
                        if field_info and field_info.json_schema_extra:
                            extra = field_info.json_schema_extra
                            if 'dims' in extra:
                                result['dims'] = extra['dims']
                            if 'similarity' in extra:
                                result['similarity'] = extra['similarity']

                    return result

            raise ValueError('Union is not supported as ES field type!')

        # We don't use Optional in ES, but its child
        if origin is Optional:
            return get_field_data(args[0])

        # List types
        if origin is list:
            arg = args[0]

            # Python type
            try:
                return {'type': _pydantic_type_map[arg]}
            except KeyError:
                pass

            # ESORM type
            if hasattr(arg, '__es_type__'):
                return {'type': arg.__es_type__}
            else:
                sub_origin = get_origin(arg)
                if sub_origin is Union:
                    try:
                        sub_arg = get_args(arg)[0]
                        return {'type': sub_arg.__es_type__}
                    except IndexError:
                        pass
                    raise ValueError(f'Unsupported ES field type: {arg}')

            # Nested class
            properties = {}
            create_mapping(arg, properties)
            return {
                'type': 'nested',
                'properties': properties
            }

        # String literals
        if origin is Literal:
            return {'type': 'keyword'}

        # Pydantic annotated types (e.g. HttpUrl in <v2.10.0)
        if origin is Annotated:
            return get_field_data(args[0])

        # Origin could be a base type as well in older Python versions
        if origin in [int, float, str, bool]:
            return {'type': _pydantic_type_map[origin]}

        # Not supported origin type
        if origin:
            raise ValueError(
                f'Unsupported ES field type: {pydantic_type}, origin: {origin}')

        # Nested class
        if issubclass(pydantic_type, BaseModel):
            # If it is a model but has an es_type, use it (e.g. geo_point)
            if hasattr(pydantic_type, '__es_type__'):
                return {'type': pydantic_type.__es_type__}

            properties = {}
            create_mapping(pydantic_type, properties)
            return {'properties': properties}

        # IntEnum type as integer
        if issubclass(pydantic_type, IntEnum):
            return {'type': 'integer'}

        # Other Enum types as keyword
        if issubclass(pydantic_type, Enum):
            return {'type': 'keyword'}

        # Is it an ESORM type?
        if hasattr(pydantic_type, '__es_type__'):
            result = {'type': pydantic_type.__es_type__}

            # Handle dense_vector specific parameters
            if pydantic_type.__es_type__ == 'dense_vector':
                field_info = next((f for f in pydantic_type.model_fields.values()
                                   if f.annotation == pydantic_type), None)
                if field_info and field_info.json_schema_extra:
                    extra = field_info.json_schema_extra
                    if 'dims' in extra:
                        result['dims'] = extra['dims']
                    if 'similarity' in extra:
                        result['similarity'] = extra['similarity']

            return result

        if issubclass(pydantic_type, AnyUrl):
            return {'type': 'keyword'}

        # Python type
        try:
            # noinspection PyTypeChecker
            return {'type': _pydantic_type_map[pydantic_type]}
        except KeyError:
            pass

        raise ValueError(
            f'Unknown ES field type: {pydantic_type} (origin: {origin}, args: {args})')

    # noinspection PyShadowingNames
    def create_mapping(model: Type[BaseModel], properties: dict):
        """ Creates mapping for the model """
        field_info: FieldInfo
        for name, field_info in model.model_fields.items():
            # Skip id field, because it won't be stored
            if hasattr(model, 'ESConfig') and model.ESConfig.id_field == name:
                continue
            # Alias support
            if field_info.alias:
                name = field_info.alias
            # Get extra field info
            extra = field_info.json_schema_extra or {}
            # Process field
            res = get_field_data(field_info.annotation)
            _type = res.get('type', None)
            if 'index' in extra and _type != 'binary':
                if 'properties' in res:
                    for v in res['properties'].values():
                        v['index'] = extra['index']
                else:
                    res['index'] = extra['index']
            # Add subfields if specified
            if 'fields' in extra:
                res['fields'] = extra['fields']
            properties[name] = res

    return create_mapping
