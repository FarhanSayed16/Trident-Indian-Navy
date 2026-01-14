/**
 * Analytics Page
 * Displays system performance, model accuracy, and baseline statistics
 */

import React, { useState, useEffect } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts'
import Card from '../components/Common/Card'
import LoadingSpinner from '../components/Common/LoadingSpinner'
import ErrorMessage from '../components/Common/ErrorMessage'
import EmptyState from '../components/Common/EmptyState'
import CardSkeleton from '../components/Common/CardSkeleton'
import ExportButton from '../components/Common/ExportButton'
import DateRangePicker from '../components/Common/DateRangePicker'
import { exportToJSON, exportToCSV, downloadCSV } from '../utils/export'
import { getMetrics, getModelMetrics, getBaselines, getAlerts } from '../services/api'

// Enhanced color palette for charts
const COLORS = [
  '#3B82F6', // Primary Blue
  '#10B981', // Success Green
  '#F59E0B', // Warning Amber
  '#EF4444', // Danger Red
  '#8B5CF6', // Purple
  '#06B6D4', // Cyan
  '#F97316', // Orange
]

// Chart styling configuration
const chartConfig = {
  grid: {
    stroke: '#E5E7EB',
    strokeWidth: 1,
    strokeDasharray: '3 3',
  },
  axis: {
    stroke: '#9CA3AF',
    strokeWidth: 1,
    fontSize: 12,
    fill: '#6B7280',
  },
  tooltip: {
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    border: 'none',
    borderRadius: '8px',
    padding: '12px',
    fontSize: '14px',
  },
}

const Analytics = () => {
  const [metrics, setMetrics] = useState(null)
  const [modelMetrics, setModelMetrics] = useState(null)
  const [baselines, setBaselines] = useState([])
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [timeRange, setTimeRange] = useState('24h') // 24h, 7d, 30d
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [dateRange, setDateRange] = useState({
    startDate: null,
    endDate: null,
  })

  const fetchAnalytics = async () => {
    try {
      setError(null)
      setLoading(true)
      
      // Fetch all metrics with proper error handling
      const [metricsRes, modelRes, baselinesRes, alertsRes] = await Promise.allSettled([
        getMetrics(),
        getModelMetrics(),
        getBaselines(),
        getAlerts({ limit: 1000 })
      ])
      
      // Handle metrics response
      if (metricsRes.status === 'fulfilled' && metricsRes.value?.data) {
        const metricsData = metricsRes.value.data
        // Validate metrics structure
        if (metricsData && typeof metricsData === 'object') {
          console.log('Metrics data received:', metricsData)
          setMetrics(metricsData)
          // Also extract model_performance if it exists in metrics
          if (metricsData.model_performance && !modelRes.value?.data) {
            console.log('Model performance from metrics:', metricsData.model_performance)
            setModelMetrics(metricsData.model_performance)
          }
        } else {
          console.warn('Invalid metrics data structure:', metricsData)
          setMetrics(null)
        }
      } else {
        console.warn('Failed to fetch metrics:', metricsRes.reason || metricsRes.status)
        setMetrics(null)
      }
      
      // Handle model metrics response (separate endpoint, or use from metrics if available)
      if (modelRes.status === 'fulfilled' && modelRes.value?.data) {
        const modelData = modelRes.value.data
        // Validate model metrics structure
        if (modelData && typeof modelData === 'object') {
          console.log('Model metrics data received:', modelData)
          setModelMetrics(modelData)
        } else {
          console.warn('Invalid model metrics data structure:', modelData)
          // Don't set to null if we have it from metrics
          if (!metricsRes.value?.data?.model_performance) {
            setModelMetrics(null)
          }
        }
      } else {
        console.warn('Failed to fetch model metrics:', modelRes.reason || modelRes.status)
        // Don't set to null if we have it from metrics
        if (!metricsRes.value?.data?.model_performance) {
          setModelMetrics(null)
        }
      }
      
      // Handle baselines response - API returns { baselines: [...], total: ... }
      if (baselinesRes.status === 'fulfilled' && baselinesRes.value?.data) {
        const baselinesData = baselinesRes.value.data
        // Check if it's the response object with baselines property
        if (baselinesData.baselines && Array.isArray(baselinesData.baselines)) {
          setBaselines(baselinesData.baselines)
        } else if (Array.isArray(baselinesData)) {
          // Fallback: if it's already an array
          setBaselines(baselinesData)
        } else {
          setBaselines([])
        }
      } else {
        console.warn('Failed to fetch baselines:', baselinesRes.reason)
        setBaselines([])
      }
      
      // Handle alerts response
      if (alertsRes.status === 'fulfilled' && alertsRes.value?.data) {
        // Alerts API might return array directly or wrapped
        const alertsData = Array.isArray(alertsRes.value.data) ? alertsRes.value.data : []
        setAlerts(alertsData)
      } else {
        console.warn('Failed to fetch alerts:', alertsRes.reason)
        setAlerts([])
      }
      
      // Only set error if all requests failed
      if (metricsRes.status === 'rejected' && modelRes.status === 'rejected' && 
          baselinesRes.status === 'rejected' && alertsRes.status === 'rejected') {
        setError('Failed to load analytics data. Please check your connection and try again.')
      }
    } catch (err) {
      console.error('Error fetching analytics:', err)
      setError('Failed to load analytics data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnalytics()
    
    if (autoRefresh) {
      const interval = setInterval(fetchAnalytics, 30000) // 30 seconds
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  // Calculate accuracy metrics from alerts
  const calculateAccuracyMetrics = () => {
    // Calculate TP/FP/TN/FN from alert statuses
    const tp = alerts.filter(a => a.status === 'true_positive').length
    const fp = alerts.filter(a => a.status === 'false_positive').length
    // TN and FN are harder to calculate without knowing all non-alerted traffic
    // For now, we'll estimate based on alerts only
    const tn = 0 // True Negatives (would need total traffic - alerts)
    const fn = 0 // False Negatives (would need ground truth data)
    
    // Calculate metrics based on alerts with feedback
    const totalWithFeedback = tp + fp
    const accuracy = totalWithFeedback > 0 ? ((tp) / totalWithFeedback) * 100 : 0
    const precision = (tp + fp) > 0 ? (tp / (tp + fp)) * 100 : 0
    const recall = (tp + fn) > 0 ? (tp / (tp + fn)) * 100 : 0
    const f1Score = (precision + recall) > 0 ? (2 * precision * recall) / (precision + recall) : 0
    const fpRate = totalWithFeedback > 0 ? (fp / totalWithFeedback) * 100 : 0
    
    return {
      tp,
      fp,
      tn,
      fn,
      total: alerts.length,
      totalWithFeedback,
      accuracy,
      precision,
      recall,
      f1Score,
      fpRate
    }
  }

  // Generate FP rate over time data (mock - replace with actual time series data)
  const getFPRateOverTime = () => {
    const data = []
    const now = new Date()
    for (let i = 23; i >= 0; i--) {
      const date = new Date(now.getTime() - i * 60 * 60 * 1000)
      data.push({
        time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        fpRate: Math.random() * 5 + 1, // Mock data: 1-6% FP rate
        accuracy: 90 + Math.random() * 8 // Mock data: 90-98% accuracy
      })
    }
    return data
  }

  // Generate model performance over time (mock - replace with actual data)
  const getModelPerformanceOverTime = () => {
    const data = []
    const now = new Date()
    for (let i = 6; i >= 0; i--) {
      const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000)
      data.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        accuracy: 92 + Math.random() * 5,
        precision: 88 + Math.random() * 8,
        recall: 85 + Math.random() * 10
      })
    }
    return data
  }

  const accuracyMetrics = calculateAccuracyMetrics()
  const fpRateData = getFPRateOverTime()
  const modelPerformanceData = getModelPerformanceOverTime()

  // Prepare confusion matrix data
  const confusionMatrixData = [
    { name: 'True Positive', value: accuracyMetrics.tp, color: COLORS[1] },
    { name: 'False Positive', value: accuracyMetrics.fp, color: COLORS[3] },
    { name: 'True Negative', value: accuracyMetrics.tn, color: COLORS[0] },
    { name: 'False Negative', value: accuracyMetrics.fn, color: COLORS[2] }
  ].filter(item => item.value > 0)

  // Prepare baseline statistics
  const baselineStats = (Array.isArray(baselines) ? baselines : []).slice(0, 10).map(baseline => ({
    context: baseline.context_type === 'ip' ? baseline.context_key : (baseline.context_key ? baseline.context_key.substring(0, 30) : 'global'),
    metrics: Object.keys(baseline.metrics || {}).length,
    version: baseline.version || 'N/A',
    updated: baseline.window_end ? new Date(baseline.window_end).toLocaleDateString() : 'N/A'
  }))

  // Check if there's any data to display
  const hasData = !!(
    (metrics && Object.keys(metrics).length > 0) || 
    (modelMetrics && Object.keys(modelMetrics).length > 0) || 
    (Array.isArray(baselines) && baselines.length > 0) || 
    (Array.isArray(alerts) && alerts.length > 0)
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics</h1>
          <p className="text-gray-600">View system performance, model accuracy, and baseline trends</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="custom">Custom Range</option>
          </select>
          {timeRange === 'custom' && (
            <DateRangePicker
              startDate={dateRange.startDate}
              endDate={dateRange.endDate}
              onChange={setDateRange}
            />
          )}
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm text-gray-600">Auto-refresh</span>
          </label>
        </div>
      </div>

      {error && (
        <ErrorMessage
          title="Error Loading Analytics"
          message={error}
          onRetry={fetchAnalytics}
        />
      )}

      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      )}

      {!loading && !error && !hasData && (
        <EmptyState
          icon="analytics"
          title="No Analytics Data Available"
          message="Analytics data will appear here once the system starts processing traffic and generating alerts."
          helpText="Make sure the backend is running and traffic is being processed."
        />
      )}

      {!loading && !error && hasData && (
        <>
          {/* Key Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <div className="text-sm text-gray-600 mb-1">Detection Accuracy</div>
              <div className="text-3xl font-bold text-gray-900">
                {accuracyMetrics.accuracy.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {accuracyMetrics.total} total detections
              </div>
            </Card>

            <Card>
              <div className="text-sm text-gray-600 mb-1">False Positive Rate</div>
              <div className="text-3xl font-bold text-orange-600">
                {accuracyMetrics.fpRate.toFixed(2)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {accuracyMetrics.fp} false positives
              </div>
            </Card>

            <Card>
              <div className="text-sm text-gray-600 mb-1">Precision</div>
              <div className="text-3xl font-bold text-blue-600">
                {accuracyMetrics.precision.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">
                TP / (TP + FP)
              </div>
            </Card>

            <Card>
              <div className="text-sm text-gray-600 mb-1">Recall</div>
              <div className="text-3xl font-bold text-green-600">
                {accuracyMetrics.recall.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">
                TP / (TP + FN)
              </div>
            </Card>
          </div>

          {/* Accuracy Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Confusion Matrix */}
            <Card title="Confusion Matrix" subtitle="TP/FP/TN/FN Distribution">
              {confusionMatrixData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={confusionMatrixData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      innerRadius={50}
                      fill="#8884d8"
                      dataKey="value"
                      paddingAngle={2}
                    >
                      {confusionMatrixData.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={entry.color}
                          stroke="#fff"
                          strokeWidth={2}
                        />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={chartConfig.tooltip} />
                    <Legend wrapperStyle={{ paddingTop: '10px' }} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No detection data available yet
                </div>
              )}
            </Card>

            {/* TP/FP/TN/FN Counts */}
            <Card title="Detection Counts" subtitle="Breakdown by category">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="font-medium text-green-900">True Positives</span>
                  <span className="text-2xl font-bold text-green-600">{accuracyMetrics.tp}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                  <span className="font-medium text-red-900">False Positives</span>
                  <span className="text-2xl font-bold text-red-600">{accuracyMetrics.fp}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="font-medium text-blue-900">True Negatives</span>
                  <span className="text-2xl font-bold text-blue-600">{accuracyMetrics.tn}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                  <span className="font-medium text-orange-900">False Negatives</span>
                  <span className="text-2xl font-bold text-orange-600">{accuracyMetrics.fn}</span>
                </div>
                <div className="pt-2 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-gray-900">Total</span>
                    <span className="text-xl font-bold text-gray-900">{accuracyMetrics.total}</span>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* FP Rate Over Time */}
          <Card title="False Positive Rate Over Time" subtitle={`Last ${timeRange}`}>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={fpRateData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis label={{ value: 'FP Rate (%)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="fpRate"
                  stroke="#F59E0B"
                  fill="#F59E0B"
                  fillOpacity={0.6}
                  name="False Positive Rate"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          {/* Model Performance */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Model Accuracy Over Time */}
            <Card title="Model Accuracy Over Time" subtitle="Last 7 days">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={modelPerformanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="accuracy"
                    stroke="#3B82F6"
                    strokeWidth={2}
                    name="Accuracy"
                  />
                  <Line
                    type="monotone"
                    dataKey="precision"
                    stroke="#10B981"
                    strokeWidth={2}
                    name="Precision"
                  />
                  <Line
                    type="monotone"
                    dataKey="recall"
                    stroke="#F59E0B"
                    strokeWidth={2}
                    name="Recall"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>

            {/* Model Performance Metrics */}
            {(modelMetrics || (metrics && metrics.model_performance)) && (
              <Card title="Model Performance Metrics" subtitle="Current model statistics">
                <div className="space-y-4">
                  {(() => {
                    const perf = modelMetrics || (metrics && metrics.model_performance) || {}
                    return (
                      <>
                        {(perf.anomaly_count !== undefined) && (
                          <div className="p-3 bg-gray-50 rounded-lg">
                            <div className="text-sm text-gray-600 mb-1">Anomalies Detected</div>
                            <div className="text-2xl font-bold text-gray-900">
                              {perf.anomaly_count}
                            </div>
                          </div>
                        )}
                        {(perf.normal_count !== undefined) && (
                          <div className="p-3 bg-gray-50 rounded-lg">
                            <div className="text-sm text-gray-600 mb-1">Normal Detections</div>
                            <div className="text-2xl font-bold text-green-600">
                              {perf.normal_count}
                            </div>
                          </div>
                        )}
                        {(perf.total_predictions !== undefined) && (
                          <div className="p-3 bg-gray-50 rounded-lg">
                            <div className="text-sm text-gray-600 mb-1">Total Predictions</div>
                            <div className="text-2xl font-bold text-gray-900">
                              {perf.total_predictions}
                            </div>
                          </div>
                        )}
                        {(perf.average_anomaly_score !== undefined) && (
                          <div className="p-3 bg-gray-50 rounded-lg">
                            <div className="text-sm text-gray-600 mb-1">Avg Anomaly Score</div>
                            <div className="text-2xl font-bold text-gray-900">
                              {(perf.average_anomaly_score * 100).toFixed(2)}%
                            </div>
                          </div>
                        )}
                        {(perf.anomaly_rate_percent !== undefined) && (
                          <div className="p-3 bg-gray-50 rounded-lg">
                            <div className="text-sm text-gray-600 mb-1">Anomaly Rate</div>
                            <div className="text-2xl font-bold text-gray-900">
                              {perf.anomaly_rate_percent.toFixed(2)}%
                            </div>
                          </div>
                        )}
                        {(!perf.total_predictions || perf.total_predictions === 0) && (
                          <div className="text-center py-4 text-sm text-gray-500">
                            No model predictions recorded yet
                          </div>
                        )}
                      </>
                    )
                  })()}
                </div>
              </Card>
            )}
          </div>

          {/* Baseline Statistics */}
          <Card title="Baseline Statistics" subtitle={`${baselines.length} baseline(s) available`}>
            {baselines.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Context
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Metrics Count
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Version
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Updated
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {baselineStats.map((baseline, index) => (
                      <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {baseline.context}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {baseline.metrics}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {baseline.version}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {baseline.updated}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No baseline data available
              </div>
            )}
          </Card>

          {/* System Performance Metrics */}
          {metrics && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Latency Metrics */}
              {metrics.latency && (
                <Card title="Detection Latency" subtitle="Response time statistics">
                  <div className="space-y-3">
                    {(metrics.latency.mean !== undefined && metrics.latency.mean !== null) && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Mean</span>
                        <span className="text-lg font-semibold text-gray-900">
                          {metrics.latency.mean.toFixed(2)}ms
                        </span>
                      </div>
                    )}
                    {(metrics.latency.median !== undefined && metrics.latency.median !== null) && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Median</span>
                        <span className="text-lg font-semibold text-gray-900">
                          {metrics.latency.median.toFixed(2)}ms
                        </span>
                      </div>
                    )}
                    {(metrics.latency.p95 !== undefined && metrics.latency.p95 !== null) && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">95th Percentile</span>
                        <span className="text-lg font-semibold text-gray-900">
                          {metrics.latency.p95.toFixed(2)}ms
                        </span>
                      </div>
                    )}
                    {(metrics.latency.p99 !== undefined && metrics.latency.p99 !== null) && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">99th Percentile</span>
                        <span className="text-lg font-semibold text-gray-900">
                          {metrics.latency.p99.toFixed(2)}ms
                        </span>
                      </div>
                    )}
                    {(metrics.latency.count !== undefined) && (
                      <div className="flex justify-between items-center pt-2 border-t border-gray-200">
                        <span className="text-xs text-gray-500">Sample Count</span>
                        <span className="text-sm font-medium text-gray-700">
                          {metrics.latency.count}
                        </span>
                      </div>
                    )}
                    {(!metrics.latency.count || metrics.latency.count === 0) && (
                      <div className="text-center py-4 text-sm text-gray-500">
                        No latency data available yet
                      </div>
                    )}
                  </div>
                </Card>
              )}

              {/* Throughput Metrics */}
              {metrics.throughput && (
                <Card title="Throughput" subtitle="Requests per second">
                  <div className="space-y-3">
                    {(metrics.throughput.requests_per_second !== undefined) && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Current Rate</span>
                        <span className="text-lg font-semibold text-gray-900">
                          {metrics.throughput.requests_per_second.toFixed(2)} req/s
                        </span>
                      </div>
                    )}
                    {(metrics.throughput.requests_in_window !== undefined) && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">In Window</span>
                        <span className="text-lg font-semibold text-gray-900">
                          {metrics.throughput.requests_in_window.toLocaleString()} requests
                        </span>
                      </div>
                    )}
                    {(metrics.throughput.total_requests !== undefined) && (
                      <div className="flex justify-between items-center pt-2 border-t border-gray-200">
                        <span className="text-sm text-gray-600">Total Requests</span>
                        <span className="text-lg font-semibold text-gray-900">
                          {metrics.throughput.total_requests.toLocaleString()}
                        </span>
                      </div>
                    )}
                    {(metrics.throughput.total_successful !== undefined) && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Successful</span>
                        <span className="text-lg font-semibold text-green-600">
                          {metrics.throughput.total_successful.toLocaleString()}
                        </span>
                      </div>
                    )}
                    {(metrics.throughput.total_failed !== undefined) && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Failed</span>
                        <span className="text-lg font-semibold text-red-600">
                          {metrics.throughput.total_failed.toLocaleString()}
                        </span>
                      </div>
                    )}
                    {(!metrics.throughput.total_requests || metrics.throughput.total_requests === 0) && (
                      <div className="text-center py-4 text-sm text-gray-500">
                        No throughput data available yet
                      </div>
                    )}
                  </div>
                </Card>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default Analytics
