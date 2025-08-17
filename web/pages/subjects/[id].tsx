import { Layout } from "../_layout";
import { PageProps } from "../_shared";

export const SubjectDetailPage = (props: PageProps) => {
    return (
        <Layout path={props.path}>
            <h1>Subject Detail</h1>
        </Layout>
    );
}