import React, { useEffect, useState } from 'react';
import api from '../api';
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
} from 'recharts';

// How many recent trades to plot. There's no API pagination yet, so we
// over-fetch ordered by -timestamp and slice client-side.
const MAX_POINTS = 40;

const formatTime = (ms) =>
    new Date(ms).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

const ChartTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload.length) return null;
    const point = payload[0].payload;
    return (
        <div
            style={{
                background: '#1e1e1e',
                border: '1px solid #333',
                borderRadius: 4,
                padding: '6px 10px',
            }}
        >
            <div style={{ color: '#888', fontSize: '0.75rem' }}>{formatTime(point.time)}</div>
            <div style={{ color: '#e0e0e0', fontWeight: 'bold', fontSize: '0.9rem' }}>
                ${point.price.toFixed(2)}
            </div>
        </div>
    );
};

const StockChart = ({ ticker }) => {
    const [trades, setTrades] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!ticker) return;
        let cancelled = false;

        const fetchTrades = async () => {
            try {
                const response = await api.get('transactions/', {
                    params: { search: ticker, ordering: '-timestamp' },
                });
                if (cancelled) return;

                const points = response.data
                    .slice(0, MAX_POINTS)
                    .map((tx) => ({
                        time: new Date(tx.timestamp).getTime(),
                        price: Number(tx.price),
                    }))
                    .reverse(); // oldest -> newest, left to right

                setTrades(points);
            } catch (error) {
                console.error('Error fetching trade history:', error);
            } finally {
                if (!cancelled) setLoading(false);
            }
        };

        setLoading(true);
        fetchTrades();
        const interval = setInterval(fetchTrades, 3000);

        return () => {
            cancelled = true;
            clearInterval(interval);
        };
    }, [ticker]);

    if (!ticker) {
        return <div style={{ padding: '20px', color: '#888' }}>Select a stock to view its chart</div>;
    }

    if (loading) {
        return <div style={{ padding: '20px', color: '#888' }}>Loading chart...</div>;
    }

    if (trades.length === 0) {
        return (
            <div style={{ padding: '20px', textAlign: 'center', color: '#444' }}>
                No trades yet for {ticker}
            </div>
        );
    }

    const prices = trades.map((t) => t.price);
    const first = prices[0];
    const last = prices[prices.length - 1];
    const isUp = last >= first;
    const color = isUp ? '#4caf50' : '#f44336';
    const deltaPct = first === 0 ? 0 : ((last - first) / first) * 100;

    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const pad = (max - min) * 0.15 || Math.max(max * 0.01, 0.5);
    const domain = [min - pad, max + pad];

    return (
        <div style={{ padding: '14px 0 4px' }}>
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'baseline',
                    marginBottom: 8,
                }}
            >
                <div>
                    <span style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#fff' }}>
                        ${last.toFixed(2)}
                    </span>
                    <span style={{ marginLeft: 10, fontSize: '0.85rem', color }}>
                        {isUp ? '▲' : '▼'} {Math.abs(deltaPct).toFixed(2)}%
                    </span>
                </div>
                <span style={{ fontSize: '0.75rem', color: '#666' }}>Last {trades.length} trades</span>
            </div>

            <ResponsiveContainer width="100%" height={170}>
                <AreaChart data={trades} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
                    <defs>
                        <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor={color} stopOpacity={0.35} />
                            <stop offset="100%" stopColor={color} stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid stroke="#262626" vertical={false} />
                    <XAxis
                        dataKey="time"
                        type="number"
                        domain={['dataMin', 'dataMax']}
                        tickFormatter={formatTime}
                        stroke="#444"
                        tick={{ fontSize: 11, fill: '#666' }}
                        axisLine={{ stroke: '#333' }}
                        tickLine={false}
                        minTickGap={50}
                    />
                    <YAxis
                        domain={domain}
                        stroke="#444"
                        tick={{ fontSize: 11, fill: '#666' }}
                        axisLine={false}
                        tickLine={false}
                        width={52}
                        tickFormatter={(v) => `$${v.toFixed(2)}`}
                    />
                    <Tooltip content={<ChartTooltip />} />
                    <Area
                        type="monotone"
                        dataKey="price"
                        stroke={color}
                        strokeWidth={2}
                        fill="url(#priceFill)"
                        dot={false}
                        isAnimationActive={false}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};

export default StockChart;