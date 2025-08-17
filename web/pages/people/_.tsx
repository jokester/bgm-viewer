import { SearchPerson } from "../../src/search/search-person";
import { Layout } from "../_layout";
import { PageProps } from "../_shared";

export function PeoplePage(props: PageProps) {
  return <Layout path={props.path}>
    <SearchPerson />
    </Layout>
}
