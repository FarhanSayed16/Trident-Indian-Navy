/**
 * Recommendation Detail Component
 * Displays detailed information about a recommendation with impact preview
 */

import React, { useState, useEffect } from 'react'
import { getRecommendation, approveRecommendation, rejectRecommendation } from '../../services/api'
import { useToastContext } from '../../context/ToastContext'
import Card from '../Common/Card'
import LoadingSpinner from '../Common/LoadingSpinner'
import ErrorMessage from '../Common/ErrorMessage'
import Modal from '../Common/Modal'

const RecommendationDetail = ({ recommendationId, onClose, onUpdate }) => {
  const { showToast } = useToastContext()
  const [recommendation, setRecommendation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [updating, setUpdating] = useState(false)
  const [showApproveDialog, setShowApproveDialog] = useState(false)
  const [showRejectDialog, setShowRejectDialog] = useState(false)
  const [rejectionReason, setRejectionReason] = useState('')
  const [approverName, setApproverName] = useState('')

  useEffect(() => {
    if (recommendationId) {
      fetchRecommendationDetails()
    }
  }, [recommendationId])

  const fetchRecommendationDetails = async () => {
    try {
      setError(null)
      setLoading(true)
      
      console.log('Fetching recommendation details for ID:', recommendationId)
      const response = await getRecommendation(recommendationId)
      console.log('Recommendation details response:', response)
      
      // API returns data directly in response.data
      if (response.data) {
        setRecommendation(response.data)
      } else {
        console.warn('No data in response:', response)
        setError('Recommendation data not found in response')
      }
    } catch (err) {
      console.error('Error fetching recommendation details:', err)
      console.error('Error details:', err.response?.data || err.message)
      setError(`Failed to load recommendation details: ${err.response?.data?.detail || err.message || 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async () => {
    if (!approverName.trim()) {
      showToast('Please enter your name', 'warning')
      return
    }

    try {
      setUpdating(true)
      await approveRecommendation(recommendationId, { approved_by: approverName })
      setShowApproveDialog(false)
      setApproverName('')
      showToast('Recommendation approved successfully', 'success')
      await fetchRecommendationDetails()
      if (onUpdate) onUpdate()
    } catch (err) {
      console.error('Error approving recommendation:', err)
      showToast('Failed to approve recommendation', 'error')
    } finally {
      setUpdating(false)
    }
  }

  const handleReject = async () => {
    if (!approverName.trim()) {
      showToast('Please enter your name', 'warning')
      return
    }
    if (!rejectionReason.trim()) {
      showToast('Please provide a rejection reason', 'warning')
      return
    }

    try {
      setUpdating(true)
      await rejectRecommendation(recommendationId, {
        approved_by: approverName,
        rejection_reason: rejectionReason
      })
      setShowRejectDialog(false)
      setApproverName('')
      setRejectionReason('')
      showToast('Recommendation rejected', 'success')
      await fetchRecommendationDetails()
      if (onUpdate) onUpdate()
    } catch (err) {
      console.error('Error rejecting recommendation:', err)
      showToast('Failed to reject recommendation', 'error')
    } finally {
      setUpdating(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-gradient-to-r from-amber-100 to-yellow-100 text-amber-800 border border-amber-300',
      approved: 'bg-gradient-to-r from-emerald-100 to-green-100 text-emerald-800 border border-emerald-300',
      rejected: 'bg-gradient-to-r from-rose-100 to-red-100 text-rose-800 border border-rose-300',
      deployed: 'bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800 border border-blue-300',
    }
    return colors[status?.toLowerCase()] || colors.pending
  }

  const getRuleTypeColor = (ruleType) => {
    const colors = {
      rate_limit: 'bg-gradient-to-r from-purple-100 to-violet-100 text-purple-800 border border-purple-300',
      ip_block: 'bg-gradient-to-r from-red-100 to-rose-100 text-red-800 border border-red-300',
      pattern_match: 'bg-gradient-to-r from-orange-100 to-amber-100 text-orange-800 border border-orange-300',
      challenge: 'bg-gradient-to-r from-blue-100 to-cyan-100 text-blue-800 border border-blue-300',
      custom: 'bg-gradient-to-r from-gray-100 to-slate-100 text-gray-800 border border-gray-300',
    }
    return colors[ruleType?.toLowerCase()] || colors.custom
  }


  if (!recommendationId) {
    return (
      <Card className="h-full flex items-center justify-center">
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
          </div>
          <p className="text-sm font-medium text-gray-600">Select a recommendation</p>
          <p className="text-xs text-gray-500 mt-1">Click on a recommendation from the list to view details</p>
        </div>
      </Card>
    )
  }

  if (loading) {
    return <LoadingSpinner text="Loading recommendation details..." />
  }

  if (error) {
    return (
      <ErrorMessage
        title="Error Loading Recommendation"
        message={error}
        onRetry={fetchRecommendationDetails}
      />
    )
  }

  if (!recommendation) {
    return (
      <Card>
        <p className="text-center text-gray-500 py-8">Recommendation not found</p>
      </Card>
    )
  }

  const impact = recommendation.estimated_impact

  return (
    <div className="space-y-3 h-full overflow-y-auto">
      {/* Enhanced Header with Better Colors */}
      <Card className="border-l-4 border-l-indigo-600 shadow-md">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-lg font-bold text-gray-900">Recommendation #{recommendation.id}</h2>
            <p className="text-xs text-gray-500 mt-0.5">{new Date(recommendation.created_at).toLocaleString()}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full p-1.5 transition-colors"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Status and Confidence - Enhanced */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-2 bg-gray-50 rounded-lg border border-gray-200">
            <label className="block text-xs font-semibold text-gray-600 mb-1.5">Status</label>
            <span className={`inline-flex px-3 py-1.5 text-xs font-bold rounded-lg shadow-sm ${getStatusColor(recommendation.status)}`}>
              {recommendation.status?.toUpperCase()}
            </span>
          </div>
          <div className="p-2 bg-gray-50 rounded-lg border border-gray-200">
            <label className="block text-xs font-semibold text-gray-600 mb-1.5">Confidence</label>
            <div className="flex items-center space-x-2">
              <div className="flex-1 bg-gray-200 rounded-full h-2.5 shadow-inner">
                <div
                  className={`h-2.5 rounded-full transition-all ${
                    (recommendation.confidence || 0) >= 0.8 ? 'bg-gradient-to-r from-green-500 to-emerald-600' :
                    (recommendation.confidence || 0) >= 0.6 ? 'bg-gradient-to-r from-yellow-400 to-amber-500' : 'bg-gradient-to-r from-red-400 to-rose-500'
                  }`}
                  style={{ width: `${Math.min((recommendation.confidence || 0) * 100, 100)}%` }}
                ></div>
              </div>
              <span className="text-xs font-bold text-gray-900 min-w-[3rem]">
                {((recommendation.confidence || 0) * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>

        {/* Deployment Status - Compact */}
        {recommendation.deployed_at && (
          <div className="mt-2 p-2 bg-blue-50 rounded border border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-medium text-blue-900">Deployed</span>
                <p className="text-[10px] text-blue-700 mt-0.5">
                  {new Date(recommendation.deployed_at).toLocaleDateString()}
                </p>
              </div>
              <span className="px-1.5 py-0.5 text-[10px] font-medium rounded bg-blue-100 text-blue-800">
                Active
              </span>
            </div>
          </div>
        )}

        {/* Approval/Rejection Info - Compact */}
        {recommendation.approved_by && (
          <div className="mt-2 p-2 bg-gray-50 rounded border border-gray-200">
            <div className="text-xs text-gray-700">
              <span className="font-medium">
                {recommendation.status === 'approved' ? 'Approved' : 'Rejected'} by:
              </span>{' '}
              {recommendation.approved_by}
              {recommendation.approved_at && (
                <span className="text-gray-500 ml-1 text-[10px]">
                  {new Date(recommendation.approved_at).toLocaleDateString()}
                </span>
              )}
            </div>
            {recommendation.rejection_reason && (
              <div className="mt-1.5 text-xs text-gray-600">
                <span className="font-medium">Reason:</span> {recommendation.rejection_reason}
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Rule Details - Enhanced */}
      <Card title="Rule Configuration" subtitle={null} className="border-l-4 border-l-purple-600 shadow-md">
        <div className="space-y-3">
          <div className="p-2 bg-gray-50 rounded-lg border border-gray-200">
            <label className="block text-xs font-semibold text-gray-700 mb-1.5">Rule Type</label>
            <span className={`inline-flex px-3 py-1.5 text-xs font-bold rounded-lg shadow-sm ${getRuleTypeColor(recommendation.rule_type)}`}>
              {recommendation.rule_type?.replace('_', ' ').toUpperCase()}
            </span>
          </div>

          {recommendation.rule_content && (
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1 uppercase tracking-wide">Description</label>
              <p className="text-xs text-gray-700 bg-gray-50 p-2 rounded border border-gray-200">
                {recommendation.rule_content}
              </p>
            </div>
          )}

          {recommendation.rule_content_modsec && (
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1 uppercase tracking-wide">ModSecurity Rule</label>
              <pre className="text-[10px] bg-gray-900 text-green-400 p-2 rounded border border-gray-700 overflow-x-auto font-mono">
                {recommendation.rule_content_modsec}
              </pre>
            </div>
          )}

          {recommendation.rule_config && (
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1 uppercase tracking-wide">Configuration</label>
              <pre className="text-[10px] bg-gray-50 p-2 rounded border border-gray-200 overflow-x-auto font-mono">
                {JSON.stringify(recommendation.rule_config, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </Card>

      {/* Impact Preview - Enhanced with Better Colors */}
      {impact && (
        <Card title="Impact Estimate" subtitle={null} className="border-l-4 border-l-green-600 shadow-md">
          <div className="space-y-3">
            {/* Key Metrics - Enhanced */}
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-3 rounded-lg border-2 border-blue-300 shadow-sm">
                <div className="text-[10px] text-blue-700 font-semibold mb-1 uppercase tracking-wide">Blocked</div>
                <div className="text-xl font-bold text-blue-900">
                  {impact.estimated_blocked_requests?.toLocaleString() || 'N/A'}
                </div>
                {impact.estimated_blocked_requests && (
                  <div className="text-[10px] text-blue-600 mt-1 font-medium">
                    ~{Math.round(impact.estimated_blocked_requests / 24)}/hr
                  </div>
                )}
              </div>

              <div className="bg-gradient-to-br from-orange-50 to-amber-50 p-3 rounded-lg border-2 border-orange-300 shadow-sm">
                <div className="text-[10px] text-orange-700 font-semibold mb-1 uppercase tracking-wide">FP Rate</div>
                <div className="text-xl font-bold text-orange-900">
                  {impact.estimated_false_positive_rate ? 
                    `${(impact.estimated_false_positive_rate * 100).toFixed(1)}%` : 'N/A'}
                </div>
                {impact.fp_confidence_interval && (
                  <div className="text-[10px] text-orange-600 mt-1 font-medium">
                    CI: {((impact.fp_confidence_interval.lower || 0) * 100).toFixed(0)}-{((impact.fp_confidence_interval.upper || 0) * 100).toFixed(0)}%
                  </div>
                )}
              </div>

              <div className="bg-gradient-to-br from-purple-50 to-violet-50 p-3 rounded-lg border-2 border-purple-300 shadow-sm">
                <div className="text-[10px] text-purple-700 font-semibold mb-1 uppercase tracking-wide">Risk</div>
                <div className="text-xl font-bold text-purple-900">
                  {impact.risk_assessment_score ? 
                    impact.risk_assessment_score.toFixed(0) : 'N/A'}
                </div>
                {impact.risk_assessment_score && (
                  <div className="text-[10px] text-purple-600 mt-1 font-medium">
                    {impact.risk_assessment_score < 30 ? 'Low' :
                     impact.risk_assessment_score < 60 ? 'Med' :
                     impact.risk_assessment_score < 85 ? 'High' : 'Critical'}
                  </div>
                )}
              </div>
            </div>

            {/* Affected Request Examples - Compact */}
            {impact.affected_request_examples && impact.affected_request_examples.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-gray-700 mb-1.5 uppercase tracking-wide">Sample Affected Requests</h4>
                <div className="space-y-1">
                  {impact.affected_request_examples.slice(0, 3).map((example, index) => (
                    <div key={index} className="bg-gray-50 p-1.5 rounded border border-gray-200 text-[10px]">
                      <div className="font-medium text-gray-900">{example.method} {example.url}</div>
                      <div className="text-gray-600">IP: {example.ip_address}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Approval/Rejection Actions - Enhanced */}
      {recommendation.status === 'pending' && (
        <Card title="Actions" subtitle={null} className="border-l-4 border-l-orange-600 shadow-md">
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                Your Name
              </label>
              <input
                type="text"
                value={approverName}
                onChange={(e) => setApproverName(e.target.value)}
                placeholder="Enter your name"
                className="w-full px-3 py-2 text-sm border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-sm"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setShowApproveDialog(true)}
                className="px-4 py-2.5 text-sm font-semibold bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all shadow-md hover:shadow-lg"
              >
                ✓ Approve
              </button>
              <button
                onClick={() => setShowRejectDialog(true)}
                className="px-4 py-2.5 text-sm font-semibold bg-gradient-to-r from-red-600 to-rose-600 text-white rounded-lg hover:from-red-700 hover:to-rose-700 transition-all shadow-md hover:shadow-lg"
              >
                ✗ Reject
              </button>
            </div>
          </div>
        </Card>
      )}

      {/* Approval Confirmation Modal */}
      <Modal
        isOpen={showApproveDialog}
        onClose={() => {
          setShowApproveDialog(false)
          setApproverName('')
        }}
        title="Approve Recommendation"
        size="md"
      >
        <div className="space-y-4">
          {impact && (
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm font-semibold text-gray-900 mb-2">
                Impact Summary:
              </p>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>• Will block ~{impact.estimated_blocked_requests?.toLocaleString() || 'N/A'} requests</li>
                <li>• Estimated FP rate: {impact.estimated_false_positive_rate ? 
                  `${(impact.estimated_false_positive_rate * 100).toFixed(2)}%` : 'N/A'}</li>
                <li>• Risk score: {impact.risk_assessment_score?.toFixed(1) || 'N/A'}</li>
              </ul>
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Name (required)
            </label>
            <input
              type="text"
              value={approverName}
              onChange={(e) => setApproverName(e.target.value)}
              placeholder="Enter your name"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
            />
          </div>
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => {
                setShowApproveDialog(false)
                setApproverName('')
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              disabled={updating}
            >
              Cancel
            </button>
            <button
              onClick={handleApprove}
              disabled={updating || !approverName.trim()}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              {updating ? 'Approving...' : 'Confirm Approval'}
            </button>
          </div>
        </div>
      </Modal>

      {/* Rejection Confirmation Modal */}
      <Modal
        isOpen={showRejectDialog}
        onClose={() => {
          setShowRejectDialog(false)
          setRejectionReason('')
          setApproverName('')
        }}
        title="Reject Recommendation"
        size="md"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Name (required)
            </label>
            <input
              type="text"
              value={approverName}
              onChange={(e) => setApproverName(e.target.value)}
              placeholder="Enter your name"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 mb-4"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rejection Reason (required)
            </label>
            <textarea
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              placeholder="Explain why this recommendation is being rejected..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              rows="4"
            />
          </div>
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => {
                setShowRejectDialog(false)
                setRejectionReason('')
                setApproverName('')
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              disabled={updating}
            >
              Cancel
            </button>
            <button
              onClick={handleReject}
              disabled={updating || !approverName.trim() || !rejectionReason.trim()}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 transition-colors"
            >
              {updating ? 'Rejecting...' : 'Confirm Rejection'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default RecommendationDetail

