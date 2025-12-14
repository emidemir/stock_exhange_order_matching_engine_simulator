import React, { useEffect, useState } from 'react';
import api from '../api'; // The axios instance we created

const StockList = ({ onSelect }) => {
    const [stocks, setStocks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTicker, setActiveTicker] = useState(null);

    // Fetch stocks on load
    useEffect(() => {
        const fetchStocks = async () => {
            try {
                const response = await api.get('stocks/');
                setStocks(response.data);
                
                // Only set active ticker on first load, not every poll
                setLoading(false); 
            } catch (error) {
                console.error("Error fetching stocks:", error);
                setLoading(false);
            }
        };

        fetchStocks(); // Initial fetch

        // POLLING: Refresh prices every 3 seconds
        const interval = setInterval(fetchStocks, 3000);

        return () => clearInterval(interval);
    }, []);

    const handleSelect = (stock) => {
        setActiveTicker(stock.ticker);
        onSelect(stock.ticker);
    };

    if (loading) return <div style={{padding: 20}}>Loading Market...</div>;

    return (
        <div className="stock-list">
            {stocks.map(stock => (
                <div 
                    key={stock.id}
                    className={`list-item ${activeTicker === stock.ticker ? 'active' : ''}`}
                    onClick={() => handleSelect(stock)}
                >
                    <div style={{display: 'flex', justifyContent: 'space-between'}}>
                        <span style={{fontWeight: 'bold', color: '#fff'}}>{stock.ticker}</span>
                        <span style={{color: '#4caf50'}}>${stock.spot_price}</span>
                    </div>
                    <div style={{fontSize: '0.8rem', color: '#888'}}>
                        {stock.name} • {stock.industry}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default StockList;