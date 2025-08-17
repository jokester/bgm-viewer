import { useEffect } from 'preact/compat';
import { useRouter } from 'preact-router';
import { Layout } from './_layout';
import { PageProps } from './_shared';

export function NotFoundPage(props: PageProps) {
  const [, navigate] = useRouter();
  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/', true);
    }, 5e3);
    return () => {
      clearTimeout(timer);
    };
  }, [navigate]);
  return (
    <Layout path={props.path ?? '/not_found'}>
      <div className='container py-8 text-center'>
        {props.url} Page not found... You will be redirected in 5s.
      </div>
    </Layout>
  );
}
