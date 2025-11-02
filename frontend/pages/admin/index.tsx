'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { Upload, RefreshCw, BarChart3, LogOut, FileText } from 'lucide-react'
import { api, StatsResponse } from '../../lib/api'

export default function AdminPanel() {
  const [stats, setStats] = useState<StatsResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [xmlUrl, setXmlUrl] = useState('')
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('admin_token')
    if (!token) {
      router.push('/admin/login')
      return
    }
    loadStats()
  }, [router])

  const getToken = () => {
    return localStorage.getItem('admin_token') || ''
  }

  const loadStats = async () => {
    try {
      setIsLoading(true)
      const data = await api.admin.getStats(getToken())
      setStats(data)
    } catch (err: any) {
      if (err.response?.status === 401) {
        localStorage.removeItem('admin_token')
        router.push('/admin/login')
      } else {
        setError('?????? ???????? ??????????')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    router.push('/admin/login')
  }

  const handleIngestXML = async () => {
    try {
      setIsLoading(true)
      setError('')
      setSuccess('')
      const url = xmlUrl || undefined
      await api.admin.ingestXML(url, getToken())
      setSuccess('XML ???? ??????? ???????? ? ?????????')
      setXmlUrl('')
      loadStats()
    } catch (err: any) {
      setError(err.response?.data?.detail || '?????? ???????? XML')
    } finally {
      setIsLoading(false)
    }
  }

  const handleIngestFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    try {
      setIsLoading(true)
      setError('')
      setSuccess('')
      await api.admin.ingestFile(file, getToken())
      setSuccess(`???? ${file.name} ??????? ???????? ? ?????????`)
      loadStats()
    } catch (err: any) {
      setError(err.response?.data?.detail || '?????? ???????? ?????')
    } finally {
      setIsLoading(false)
      e.target.value = ''
    }
  }

  const handleReindex = async () => {
    if (!confirm('?? ???????? ??? ??????? ???? ??????. ??? ????? ????? ????????????? ??????.')) {
      return
    }

    try {
      setIsLoading(true)
      setError('')
      setSuccess('')
      await api.admin.reindex(getToken())
      setSuccess('?????? ??????? ??????')
      loadStats()
    } catch (err: any) {
      setError(err.response?.data?.detail || '?????? ??????????????')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">?????? ??????????????</h1>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            <LogOut className="w-5 h-5" />
            ?????
          </button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Alerts */}
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {success}
          </div>
        )}

        {/* Stats */}
        {stats && (
          <div className="mb-8 bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-6 h-6 text-primary-500" />
              <h2 className="text-xl font-semibold text-gray-800">??????????</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <StatCard title="????? ?????" value={stats.total_chats} />
              <StatCard title="?????????? ??????" value={stats.total_sources} />
              <StatCard title="??????" value={stats.total_chunks} />
              <StatCard title="???????? ? Qdrant" value={stats.qdrant_points} />
            </div>

            {stats.data_sources.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-medium text-gray-700 mb-3">????????? ??????</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          ????????
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          ???
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          ??????
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          ????
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {stats.data_sources.map((source) => (
                        <tr key={source.id}>
                          <td className="px-4 py-3 text-sm text-gray-900">{source.name}</td>
                          <td className="px-4 py-3 text-sm text-gray-500">{source.type}</td>
                          <td className="px-4 py-3 text-sm text-gray-500">{source.chunks_count}</td>
                          <td className="px-4 py-3 text-sm text-gray-500">
                            {new Date(source.created_at).toLocaleDateString('ru-RU')}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Ingest XML */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center gap-2 mb-4">
              <FileText className="w-6 h-6 text-primary-500" />
              <h2 className="text-xl font-semibold text-gray-800">???????? XML</h2>
            </div>
            <div className="space-y-4">
              <input
                type="text"
                value={xmlUrl}
                onChange={(e) => setXmlUrl(e.target.value)}
                placeholder="URL XML ????? (???????? ?????? ??? ??????????)"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <button
                onClick={handleIngestXML}
                disabled={isLoading}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50"
              >
                <Upload className="w-5 h-5" />
                ????????? XML
              </button>
            </div>
          </div>

          {/* Ingest File */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center gap-2 mb-4">
              <Upload className="w-6 h-6 text-primary-500" />
              <h2 className="text-xl font-semibold text-gray-800">???????? ?????</h2>
            </div>
            <div className="space-y-4">
              <input
                type="file"
                onChange={handleIngestFile}
                accept=".pdf,.docx,.txt,.md"
                disabled={isLoading}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <p className="text-sm text-gray-500">
                ?????????????? ???????: PDF, DOCX, TXT, Markdown
              </p>
            </div>
          </div>

          {/* Reindex */}
          <div className="bg-white rounded-lg shadow-sm p-6 md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <RefreshCw className="w-6 h-6 text-primary-500" />
              <h2 className="text-xl font-semibold text-gray-800">?????????? ????????</h2>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              ??????? ??????? ?????? ??? ?????? ?? ?????????? ?????????. ????? ????? ??? ????? ?????
              ????????????? ??? ????????? ??????.
            </p>
            <button
              onClick={handleReindex}
              disabled={isLoading}
              className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50"
            >
              ???????? ??????
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value }: { title: string; value: number }) {
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <p className="text-sm text-gray-500 mb-1">{title}</p>
      <p className="text-2xl font-bold text-gray-800">{value.toLocaleString()}</p>
    </div>
  )
}
