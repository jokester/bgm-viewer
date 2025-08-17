import { render } from 'preact/compat';
import Router from 'preact-router';
import './src/app.css';
// import "primereact/resources/themes/fluent-light/theme.css";
import debug from 'debug';
import { NotFoundPage } from './pages/404';
import { IndexPage } from './pages';
import { SubjectsPage } from './pages/subjects';
import { PrimeReactProvider } from 'primereact/api';



const logger = debug('app:main');

function RootRouter() {
  return (
    <PrimeReactProvider>

    {/* @ts-ignore */}
    <Router>
      <IndexPage path='/' />
      <SubjectsPage path='/subjects' />
      <NotFoundPage default />
    </Router></PrimeReactProvider>
  );
}
render(<RootRouter />, document.getElementById('app')!);

logger('app loaded');
