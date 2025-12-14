import React, { useEffect, useState } from 'react';
import api from '../api';

const UserList = () => {
    const [users, setUsers] = useState([]);

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const response = await api.get('users/');
                setUsers(response.data);
            } catch (error) {
                console.error("Error fetching users:", error);
            }
        };

        // Fetch once on load, then poll every 5 seconds to update balances
        fetchUsers();
        const interval = setInterval(fetchUsers, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div>
            {/* Table Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 10px', color: '#888', fontSize: '0.8rem', borderBottom: '1px solid #333' }}>
                <span>TRADER</span>
                <span>CASH</span>
            </div>

            {/* List */}
            <div style={{ padding: '0 10px' }}>
                {users.map(user => (
                    <div key={user.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #222' }}>
                        <span style={{ fontWeight: 'bold', color: '#e0e0e0' }}>
                            {user.username}
                        </span>
                        <span style={{ color: '#ffb74d', fontFamily: 'monospace' }}>
                            ${parseFloat(user.balance).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default UserList;