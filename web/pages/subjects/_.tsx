import { Layout } from "../_layout";
import { PageProps } from "../_shared";
import { SearchSubject } from "../../src/search/search-subject";

export function SubjectsPage(props: PageProps) {
    return (
        <Layout path={props.path}>
            <SearchSubject />
        </Layout>
    );
}