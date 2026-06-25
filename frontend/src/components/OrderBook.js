import React, { useEffect, useState } from 'react';
import api from '../api';

const OrderBook = ({ ticker }) => {
    const [book, setBook] = useState({ bids: [], asks: [], spread: null });
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

    // Each side is scaled against its own deepest level, so the bars stay
    // meaningful even when bids and asks have very different total size.
    const maxBidQty = Math.max(1, ...book.bids.map((l) => l.quantity));
    const maxAskQty = Math.max(1, ...book.asks.map((l) => l.quantity));

    // One row per aggregated price level (not one row per individual order).
    const renderRows = (levels, side, maxQty) => {
        const displayLevels = side === 'ask' ? [...levels].reverse() : levels;

        return displayLevels.map((level) => {
            const price = Number(level.price);
            const pct = maxQty > 0 ? Math.min(100, (level.quantity / maxQty) * 100) : 0;
            const title = `${level.order_count} order${level.order_count > 1 ? 's' : ''} at $${price.toFixed(2)}`;

            return (
                <div className="book-row" key={`${side}-${level.price}`} title={title}>
                    <div className={`depth-bar depth-bar-${side}`} style={{ width: `${pct}%` }} />
                    <span className="book-qty">{level.quantity}</span>
                    <span className={`book-price book-price-${side}`}>{price.toFixed(2)}</span>
                </div>
            );
        });
    };

    const spread = book.spread;

    return (
        <div className="order-book">
            {/* Header */}
            <div className="book-header-row">
                <span>QTY</span>
                <span>PRICE</span>
            </div>

            {/* ASKS (Sellers) — worst price at top, best (lowest) right above the spread */}
            <div>
                {book.asks.length === 0
                    ? <div className="book-empty">No sellers</div>
                    : renderRows(book.asks, 'ask', maxAskQty)}
            </div>

            {/* Spread */}
            <div className="book-spread">
                {spread ? (
                    <>
                        <span className="book-spread-label">SPREAD</span>
                        <span className="book-spread-amount">${Number(spread.amount).toFixed(2)}</span>
                        <span className="book-spread-pct">({Number(spread.percent).toFixed(2)}%)</span>
                    </>
                ) : (
                    <span className="book-spread-label">SPREAD</span>
                )}
            </div>

            {/* BIDS (Buyers) — best (highest) price at top */}
            <div>
                {book.bids.length === 0
                    ? <div className="book-empty">No buyers</div>
                    : renderRows(book.bids, 'bid', maxBidQty)}
            </div>
        </div>
    );
};

export default OrderBook;