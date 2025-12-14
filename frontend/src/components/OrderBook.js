import React, { useEffect, useState } from 'react';
import api from '../api';

const OrderBook = ({ ticker }) => {
    const [book, setBook] = useState({ bids: [], asks: [] });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!ticker) return;

        const fetchBook = async () => {
            try {
                // Don't set loading=true on every poll to avoid flickering
                const response = await api.get(`orders/book/${ticker}/`);
                setBook(response.data);
            } catch (error) {
                console.error("Error fetching order book:", error);
            }
        };

        // Initial fetch
        setLoading(true);
        fetchBook().then(() => setLoading(false));

        // Auto-refresh every 2 seconds (Polling)
        const interval = setInterval(fetchBook, 2000);

        // Cleanup on unmount or ticker change
        return () => clearInterval(interval);
    }, [ticker]);

    if (!ticker) return <div style={{ padding: 20, color: '#888' }}>Select a stock to view the Order Book</div>;
    if (loading) return <div style={{ padding: 20 }}>Loading Book...</div>;

    // Helper to render a list of orders
    const renderRows = (orders, type) => {
        // Reverse asks so the lowest sell price is at the bottom (closest to the spread)
        const displayOrders = type === 'ask' ? [...orders].reverse() : orders;
        
        return displayOrders.map((order) => (
            <div key={order.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #222' }}>
                <span style={{ width: '33%', textAlign: 'left', color: '#aaa' }}>{order.quantity}</span>
                <span style={{ 
                    width: '33%', 
                    textAlign: 'right', 
                    fontWeight: 'bold', 
                    color: type === 'bid' ? '#4caf50' : '#f44336' // Green for Bids, Red for Asks
                }}>
                    {order.price}
                </span>
            </div>
        ));
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Header / Spread */}
            <div style={{ padding: '10px 20px', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                <span style={{ color: '#888' }}>QTY</span>
                <span style={{ color: '#888' }}>PRICE</span>
            </div>

            {/* ASKS (Sellers) - Top Half */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '10px 20px', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
                {renderRows(book.asks, 'ask')}
                {book.asks.length === 0 && <div style={{textAlign: 'center', color: '#444'}}>No Sellers</div>}
            </div>

            {/* The Spread (Gap) */}
            <div style={{ padding: '5px', backgroundColor: '#263238', textAlign: 'center', fontSize: '0.8rem', color: '#bbb', letterSpacing: '1px' }}>
                SPREAD
            </div>

            {/* BIDS (Buyers) - Bottom Half */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '10px 20px' }}>
                {book.bids.length === 0 && <div style={{textAlign: 'center', color: '#444'}}>No Buyers</div>}
                {renderRows(book.bids, 'bid')}
            </div>
        </div>
    );
};

export default OrderBook;