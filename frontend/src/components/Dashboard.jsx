import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line, Scatter } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { AlertTriangle, RefreshCw, Database, BrainCircuit, Activity } from 'lucide-react';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const API_URL = 'http://localhost:8000';

const Dashboard = () => {
    const [stats, setStats] = useState(null);
    const [anomalies, setAnomalies] = useState([]);
    const [loading, setLoading] = useState(false);
    const [training, setTraining] = useState(false);
    const [evaluation, setEvaluation] = useState(null);
    const [evaluating, setEvaluating] = useState(false);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const res = await axios.get(`${API_URL}/stats`);
            setStats(res.data);
        } catch (err) {
            console.error("Error fetching stats:", err);
        }
    };

    const generateData = async () => {
        setLoading(true);
        try {
            await axios.post(`${API_URL}/generate-data`);
            await fetchStats();
            alert("Data generated successfully!");
        } catch (err) {
            console.error("Error generating data:", err);
            alert("Failed to generate data.");
        }
        setLoading(false);
    };

    const trainModels = async () => {
        setTraining(true);
        try {
            await axios.post(`${API_URL}/train`);
            alert("Models trained successfully!");
        } catch (err) {
            console.error("Error training models:", err);
            alert("Failed to train models.");
        }
        setTraining(false);
    };

    const evaluateModel = async () => {
        setEvaluating(true);
        try {
            // Evaluate Isolation Forest by default for now, or add a selector
            const res = await axios.post(`${API_URL}/evaluate?model_type=isolation_forest`);
            setEvaluation(res.data);
        } catch (err) {
            console.error("Error evaluating model:", err);
            alert("Failed to evaluate model.");
        }
        setEvaluating(false);
    };

    const detectAnomalies = async () => {
        try {
            const res = await axios.get(`${API_URL}/detect?model_type=isolation_forest`);
            setAnomalies(res.data.anomalies);
        } catch (err) {
            console.error("Error detecting anomalies:", err);
            alert("Failed to detect anomalies. Ensure models are trained.");
        }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Controls & Stats */}
            <div className="lg:col-span-1 space-y-6">
                <div className="card">
                    <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                        <Database className="w-5 h-5 text-accent-primary" />
                        Data Controls
                    </h2>
                    <div className="space-y-4">
                        <button
                            onClick={generateData}
                            disabled={loading}
                            className="w-full btn-primary flex items-center justify-center gap-2"
                        >
                            {loading ? <RefreshCw className="animate-spin w-4 h-4" /> : <RefreshCw className="w-4 h-4" />}
                            Generate Synthetic Data
                        </button>

                        <button
                            onClick={trainModels}
                            disabled={training}
                            className="w-full bg-bg-card hover:bg-bg-primary border border-white/10 text-white py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
                        >
                            {training ? <BrainCircuit className="animate-pulse w-4 h-4" /> : <BrainCircuit className="w-4 h-4" />}
                            Train Models
                        </button>

                        <button
                            onClick={detectAnomalies}
                            className="w-full bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/50 py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
                        >
                            <AlertTriangle className="w-4 h-4" />
                            Run Detection
                        </button>

                        <button
                            onClick={evaluateModel}
                            disabled={evaluating}
                            className="w-full bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 border border-blue-500/50 py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
                        >
                            {evaluating ? <Activity className="animate-spin w-4 h-4" /> : <Activity className="w-4 h-4" />}
                            Evaluate Accuracy
                        </button>
                    </div>
                </div>

                {evaluation && (
                    <div className="card">
                        <h2 className="text-xl font-semibold mb-4">Model Performance</h2>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center">
                                <span className="text-text-secondary">Accuracy</span>
                                <span className="font-mono font-bold text-accent-primary">{(evaluation.accuracy * 100).toFixed(1)}%</span>
                            </div>
                            <div className="w-full bg-bg-primary rounded-full h-2">
                                <div className="bg-accent-primary h-2 rounded-full" style={{ width: `${evaluation.accuracy * 100}%` }}></div>
                            </div>

                            <div className="flex justify-between items-center">
                                <span className="text-text-secondary">Precision</span>
                                <span className="font-mono font-bold text-green-400">{(evaluation.precision * 100).toFixed(1)}%</span>
                            </div>
                            <div className="w-full bg-bg-primary rounded-full h-2">
                                <div className="bg-green-400 h-2 rounded-full" style={{ width: `${evaluation.precision * 100}%` }}></div>
                            </div>

                            <div className="flex justify-between items-center">
                                <span className="text-text-secondary">Recall</span>
                                <span className="font-mono font-bold text-yellow-400">{(evaluation.recall * 100).toFixed(1)}%</span>
                            </div>
                            <div className="w-full bg-bg-primary rounded-full h-2">
                                <div className="bg-yellow-400 h-2 rounded-full" style={{ width: `${evaluation.recall * 100}%` }}></div>
                            </div>

                            <div className="flex justify-between items-center">
                                <span className="text-text-secondary">F1 Score</span>
                                <span className="font-mono font-bold text-purple-400">{(evaluation.f1_score * 100).toFixed(1)}%</span>
                            </div>
                            <div className="w-full bg-bg-primary rounded-full h-2">
                                <div className="bg-purple-400 h-2 rounded-full" style={{ width: `${evaluation.f1_score * 100}%` }}></div>
                            </div>
                        </div>
                    </div>
                )}

                {stats && (
                    <div className="card">
                        <h2 className="text-xl font-semibold mb-4">Statistics</h2>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center p-3 bg-bg-primary rounded-lg">
                                <span className="text-text-secondary">Total Transactions</span>
                                <span className="font-mono font-bold text-lg">{stats.total_transactions}</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-bg-primary rounded-lg">
                                <span className="text-text-secondary">Avg Amount</span>
                                <span className="font-mono font-bold text-lg">${stats.avg_amount?.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-bg-primary rounded-lg">
                                <span className="text-text-secondary">Total Volume</span>
                                <span className="font-mono font-bold text-lg">${stats.total_amount?.toLocaleString()}</span>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Visualization Area */}
            <div className="lg:col-span-2 space-y-6">
                <div className="card min-h-[400px]">
                    <h2 className="text-xl font-semibold mb-4">Anomaly Visualization</h2>
                    {anomalies.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="text-text-secondary border-b border-white/10">
                                        <th className="p-3">ID</th>
                                        <th className="p-3">Amount</th>
                                        <th className="p-3">Category</th>
                                        <th className="p-3">Location</th>
                                        <th className="p-3">Score</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {anomalies.slice(0, 10).map((txn) => (
                                        <tr key={txn.transaction_id} className="border-b border-white/5 hover:bg-white/5">
                                            <td className="p-3 font-mono text-sm">{txn.transaction_id}</td>
                                            <td className="p-3 text-accent-primary font-bold">${txn.amount}</td>
                                            <td className="p-3">{txn.category}</td>
                                            <td className="p-3">{txn.location}</td>
                                            <td className="p-3 text-red-400 font-bold">ANOMALY</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            <p className="text-center text-text-secondary mt-4 text-sm">Showing top 10 detected anomalies</p>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-text-secondary opacity-50 min-h-[300px]">
                            <Database className="w-16 h-16 mb-4" />
                            <p>No anomalies detected yet. Generate data and run detection.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
