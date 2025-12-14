import React, { useState } from 'react';
import api from '../api';

const EventControls = () => {
    const [message, setMessage] = useState(null);

    const triggerEvent = async (title, sentiment, industry = null) => {
        try {
            await api.post('events/', {
                title: title,
                sentiment_score: sentiment,
                target_industry: industry || 'GLOBAL', // Default to Global if not specific
                is_active: true
            });
            
            setMessage(`Deployed: ${title}`);
            setTimeout(() => setMessage(null), 3000); // Clear message after 3s
        } catch (error) {
            console.error("Error firing event:", error);
            setMessage("Failed to deploy event.");
        }
    };

    return (
        <div style={{ padding: '10px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            
            {/* Status Message */}
            {message && (
                <div style={{ padding: '8px', backgroundColor: '#333', color: '#4caf50', borderRadius: '4px', textAlign: 'center', fontSize: '0.9rem' }}>
                    {message}
                </div>
            )}

            {/* Button 1: Bull Market */}
            <button 
                onClick={() => triggerEvent("Fed Rate Cut", 0.30, "GLOBAL")}
                style={styles.buttonGreen}
            >
                🚀 RATE CUT (+30%)
            </button>

            {/* Button 2: Tech Crash */}
            <button 
                onClick={() => triggerEvent("AI Regulation", -0.40, "Technology")}
                style={styles.buttonRed}
            >
                📉 TECH CRASH (-40%)
            </button>

            {/* Button 3: Oil Shock */}
            <button 
                onClick={() => triggerEvent("Pipeline Boom", 0.50, "Energy")}
                style={styles.buttonYellow}
            >
                🛢️ OIL BOOM (+50%)
            </button>

            <div style={{ marginTop: '10px', fontSize: '0.8rem', color: '#666', textAlign: 'center' }}>
                Clicking these injects news into the bot brains.
            </div>
        </div>
    );
};

const styles = {
    buttonGreen: { padding: '12px', backgroundColor: '#2e7d32', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' },
    buttonRed: { padding: '12px', backgroundColor: '#c62828', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' },
    buttonYellow: { padding: '12px', backgroundColor: '#f9a825', color: 'black', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' },
};

export default EventControls;