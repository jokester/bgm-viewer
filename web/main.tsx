import { render } from 'preact/compat';
import Router from 'preact-router';
import './src/app.css';
// import "primereact/resources/themes/fluent-light/theme.css";
import debug from 'debug';
import { NotFoundPage } from './pages/404';
import { IndexPage } from './pages';
import { SubjectsPage } from './pages/subjects/_';
import { PrimeReactProvider } from 'primereact/api';
import { CharactersPage } from './pages/characters/_';
import {PeoplePage} from './pages/people/_';
import { NetworkPage } from './pages/network';



const logger = debug('app:main');

function RootRouter() {
  return (
    <PrimeReactProvider>

    {/* @ts-ignore */}
    <Router>
      <IndexPage path='/' />
      <SubjectsPage path='/subjects' />
      <CharactersPage path='/characters' />
      <PeoplePage path='/people' />
      <NetworkPage path='/network' />
      {/* @ts-ignore */}
      <NotFoundPage default />
    </Router></PrimeReactProvider>
  );
}
render(<RootRouter />, document.getElementById('app')!);

logger('app loaded');
