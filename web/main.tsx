import { render } from 'preact/compat';
import Router from 'preact-router';
import './src/app.scss';
import debug from 'debug';
import { NotFoundPage } from './pages/404';
import { IndexPage } from './pages';
import { SearchPage } from './pages/search';
import { PrimeReactProvider } from 'primereact/api';
// import "primereact/resources/themes/lara-light-cyan/theme.css";
import "primereact/resources/themes/fluent-light/theme.css";



const logger = debug('app:main');

function RootRouter() {
  return (
    <PrimeReactProvider>

    {/* @ts-ignore */}
    <Router>
      <IndexPage path='/' />
      <SearchPage path='/search' />
      <NotFoundPage default />
    </Router></PrimeReactProvider>
  );
}
render(<RootRouter />, document.getElementById('app')!);

logger('app loaded');
