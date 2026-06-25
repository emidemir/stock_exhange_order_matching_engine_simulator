import React, { useState } from 'react';
import './App.css';

import StockList from './components/StockList';
import StockChart from './components/StockChart';
import OrderBook from './components/OrderBook';
import UserList from './components/UserList';
import EventControls from './components/EventControl';

function App() {
  const [selectedTicker, setSelectedTicker] = useState(null);

  return (
    <div className="dashboard-container">

      {/* COLUMN 1: Stocks */}
      <div className="panel">
        <div className="panel-header">Market Watch</div>
        <StockList onSelect={setSelectedTicker} />
      </div>

      {/* COLUMN 2: Chart + Order Book */}
      <div className="panel book-panel">
        <div className="panel-header">
          {selectedTicker ? `Order Book: ${selectedTicker}` : 'Order Book'}
        </div>

        <div className="chart-wrap">
          <StockChart ticker={selectedTicker} />
        </div>

        <div className="book-wrap">
          <OrderBook ticker={selectedTicker} />
        </div>
      </div>

      {/* COLUMN 3: Users & Events */}
      <div className="right-column">

        {/* Top Half: Users */}
        <div className="sub-panel">
          <div className="panel-header">Market Participants</div>
          <UserList />
        </div>

        {/* Bottom Half: Events */}
        <div className="sub-panel">
          <div className="panel-header">God Mode (Events)</div>
          <EventControls />
        </div>

      </div>
    </div>
  );
}

export default App;