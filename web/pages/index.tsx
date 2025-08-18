import { Layout } from './_layout';
import { PageProps } from './_shared';

export function IndexPage(props: PageProps) {
  return (
    <Layout path={props.path}>
      <div className='container'>
        <h1>Bangumi Archive Viewer</h1>
      </div>
    </Layout>
  );
}
