# bgm-archive

Random stuff build around [bangumi/Archive](https://github.com/bangumi/Archive)

## API Endpoints

### Search Subjects
- **POST** `/subjects/search`
- **Description**: Search subjects using Elasticsearch full-text search
- **Request Body**:
  ```json
  {
    "query": "search term",
    "limit": 20,
    "offset": 0,
    "subject_type": 2,
    "nsfw": false
  }
  ```
- **Response**: List of subjects matching the search criteria

**Parameters**:
- `query` (required): Search term for full-text search across name, summary, infobox, and tags
- `limit` (optional): Maximum number of results to return (default: 20)
- `offset` (optional): Number of results to skip for pagination (default: 0)
- `subject_type` (optional): Filter by subject type (1=Book, 2=Anime, 3=Music, 4=Game, 6=Real)
- `nsfw` (optional): Filter by NSFW content (true/false)

**Search Fields**:
- `name` (weight: 3x) - Subject name
- `name_cn` (weight: 3x) - Chinese name
- `summary` (weight: 2x) - Subject summary
- `infobox` (weight: 1x) - Subject infobox
- `tags.name` (weight: 2x) - Tag names

### Search Characters
- **POST** `/characters/search`
- **Description**: Search characters using Elasticsearch full-text search
- **Request Body**:
  ```json
  {
    "query": "search term",
    "limit": 20,
    "offset": 0,
    "role": 1
  }
  ```
- **Response**: List of characters matching the search criteria

**Parameters**:
- `query` (required): Search term for full-text search across name, summary, and infobox
- `limit` (optional): Maximum number of results to return (default: 20)
- `offset` (optional): Number of results to skip for pagination (default: 0)
- `role` (optional): Filter by character role (1=Main, 2=Supporting, 3=Minor, 4=Guest)

**Search Fields**:
- `name` (weight: 3x) - Character name
- `summary` (weight: 2x) - Character summary
- `infobox` (weight: 1x) - Character infobox

## ES (Elasticsearch)