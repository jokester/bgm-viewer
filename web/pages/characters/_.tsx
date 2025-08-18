import { Layout } from '../_layout';
import { PageProps } from '../_shared';
import { SearchCharacter } from '../../src/search/search-character';

export function CharactersPage(props: PageProps) {
  return (
    <Layout path={props.path}>
      <SearchCharacter />
    </Layout>
  );
}
