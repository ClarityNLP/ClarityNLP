import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'fixed-data-table-2/dist/fixed-data-table-base.min.css';
import 'fixed-data-table-2/dist/fixed-data-table-style.min.css';
import App from './App';
import registerServiceWorker from './registerServiceWorker';

ReactDOM.render(<App />, document.getElementById('root'));
registerServiceWorker();
