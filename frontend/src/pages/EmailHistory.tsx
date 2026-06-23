import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, ChevronLeft, ChevronRight, X, Search } from 'lucide-react';
import AppShell from '../components/AppShell';

const API_BASE_URL = (process.env.REACT_APP_API_URL || 'https://inmailer.onrender.com') + '/api';

interface EmailHistoryItem {
  id: number;
  recipient_email: string;
  subject: string;
  status: string;
  sent_at: string;
  template_id: number | null;
  template_name: string | null;
  campaign_id: number | null;
  campaign_name: string | null;
  error_message: string | null;
  gmail_message_id: string | null;
}

interface PaginatedHistory {
  emails: EmailHistoryItem[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

interface GroupSummary {
  group_id: number | string | null;
  group_name: string;
  total: number;
  success_count: number;
  error_count: number;
  last_sent_at: string | null;
}

interface GroupedResponse {
  group_by: string;
  groups: GroupSummary[];
}

interface GroupDetail {
  id: number;
  recipient_email: string;
  subject: string;
  status: string;
  sent_at: string;
}

interface PaginatedGroupDetail {
  emails: GroupDetail[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

type ActiveTab = 'all' | 'grouped';
type GroupBy = 'campaign' | 'template' | 'status';
type SortOption = 'sent_at_desc' | 'sent_at_asc' | 'recipient_email_asc';

function StatusBadge({ status }: { status: string }) {
  const cls =
    status === 'sent' ? 'badge-green' :
    status === 'failed' ? 'badge-red' :
    status === 'pending' ? 'badge-yellow' :
    'badge-zinc';
  return <span className={`badge ${cls}`}>{status}</span>;
}

function TemplateBadge({ name }: { name: string | null }) {
  if (!name) return <span className="badge badge-zinc text-zinc-600">—</span>;
  return <span className="badge badge-indigo max-w-[120px] truncate" title={name}>{name}</span>;
}

function CampaignBadge({ name }: { name: string | null }) {
  if (!name) return <span className="badge badge-zinc text-zinc-600">—</span>;
  return <span className="badge bg-violet-500/10 text-violet-400 border border-violet-500/20 max-w-[120px] truncate" title={name}>{name}</span>;
}

function SkeletonRow() {
  return (
    <tr className="animate-pulse">
      {[...Array(6)].map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-3.5 bg-zinc-800 rounded w-3/4" />
        </td>
      ))}
    </tr>
  );
}

function formatDate(iso: string | null) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function formatShortDate(iso: string | null) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function EmailHistory() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<ActiveTab>('all');

  const [history, setHistory] = useState<PaginatedHistory | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');
  const [sortOption, setSortOption] = useState<SortOption>('sent_at_desc');
  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [groupBy, setGroupBy] = useState<GroupBy>('campaign');
  const [groups, setGroups] = useState<GroupSummary[]>([]);
  const [groupsLoading, setGroupsLoading] = useState(false);
  const [groupsError, setGroupsError] = useState<string | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<GroupSummary | null>(null);
  const [groupDetail, setGroupDetail] = useState<PaginatedGroupDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [detailPage, setDetailPage] = useState(1);

  const fetchHistory = useCallback(async () => {
    setHistoryLoading(true);
    setHistoryError(null);
    try {
      const [sortBy, sortOrder] = sortOption === 'sent_at_desc' ? ['sent_at', 'desc']
        : sortOption === 'sent_at_asc' ? ['sent_at', 'asc']
        : ['recipient_email', 'asc'];
      const params = new URLSearchParams({ page: String(page), per_page: '20', sort_by: sortBy, sort_order: sortOrder });
      if (statusFilter) params.set('status', statusFilter);
      if (search) params.set('search', search);
      const res = await fetch(`${API_BASE_URL}/email-history?${params}`, { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to fetch history');
      setHistory(await res.json());
    } catch {
      setHistoryError('Could not load email history. Please try again.');
    } finally {
      setHistoryLoading(false);
    }
  }, [page, statusFilter, search, sortOption]);

  useEffect(() => { if (activeTab === 'all') fetchHistory(); }, [activeTab, fetchHistory]);

  const handleSearchChange = (val: string) => {
    setSearchInput(val);
    if (searchTimer.current) clearTimeout(searchTimer.current);
    searchTimer.current = setTimeout(() => { setSearch(val); setPage(1); }, 300);
  };

  const fetchGroups = useCallback(async () => {
    setGroupsLoading(true);
    setGroupsError(null);
    setSelectedGroup(null);
    setGroupDetail(null);
    try {
      const res = await fetch(`${API_BASE_URL}/email-history/grouped?group_by=${groupBy}`, { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to fetch groups');
      const data: GroupedResponse = await res.json();
      setGroups(data.groups);
    } catch {
      setGroupsError('Could not load grouped view. Please try again.');
    } finally {
      setGroupsLoading(false);
    }
  }, [groupBy]);

  useEffect(() => { if (activeTab === 'grouped') fetchGroups(); }, [activeTab, fetchGroups]);

  const fetchGroupDetail = useCallback(async (group: GroupSummary, pg: number) => {
    setDetailLoading(true);
    setDetailError(null);
    try {
      const rawId = group.group_id === null ? 'null' : String(group.group_id);
      const res = await fetch(`${API_BASE_URL}/email-history/grouped/${groupBy}/${rawId}?page=${pg}&per_page=20`, { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to fetch group detail');
      setGroupDetail(await res.json());
    } catch {
      setDetailError('Could not load emails for this group.');
    } finally {
      setDetailLoading(false);
    }
  }, [groupBy]);

  const handleSelectGroup = (group: GroupSummary) => {
    setSelectedGroup(group);
    setDetailPage(1);
    setGroupDetail(null);
    fetchGroupDetail(group, 1);
  };

  const handleDetailPageChange = (pg: number) => {
    if (!selectedGroup) return;
    setDetailPage(pg);
    fetchGroupDetail(selectedGroup, pg);
  };

  const showingFrom = history ? (history.page - 1) * history.per_page + 1 : 0;
  const showingTo = history ? Math.min(history.page * history.per_page, history.total) : 0;

  const thCls = "px-4 py-3 text-left text-xs font-medium text-zinc-600 uppercase tracking-wide";
  const tdCls = "px-4 py-3 text-sm";

  return (
    <AppShell>
      <div className="px-6 py-8 max-w-7xl mx-auto w-full">
        {/* Header */}
        <div className="mb-8">
          <h1 className="page-title">Email History</h1>
          <p className="page-description">All emails sent through InMailer</p>
        </div>

        {/* Tab switcher */}
        <div className="flex border-b border-zinc-800 mb-6">
          {(['all', 'grouped'] as ActiveTab[]).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-5 py-3 text-sm font-medium border-b-2 transition-colors capitalize ${
                activeTab === tab
                  ? 'border-indigo-500 text-indigo-400'
                  : 'border-transparent text-zinc-500 hover:text-zinc-300'
              }`}
            >
              {tab === 'all' ? 'All emails' : 'Grouped view'}
            </button>
          ))}
        </div>

        {/* ── All Emails Tab ────────────────────────────────────────────── */}
        {activeTab === 'all' && (
          <div>
            {/* Filter bar */}
            <div className="flex flex-wrap gap-3 mb-5">
              <div className="flex-1 min-w-[200px] relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-600 pointer-events-none" />
                <input
                  type="text"
                  placeholder="Search recipient or subject…"
                  value={searchInput}
                  onChange={e => handleSearchChange(e.target.value)}
                  className="input pl-9"
                />
              </div>
              <select
                value={statusFilter}
                onChange={e => { setStatusFilter(e.target.value); setPage(1); }}
                className="input w-auto"
              >
                <option value="">All statuses</option>
                <option value="sent">Sent</option>
                <option value="failed">Failed</option>
                <option value="pending">Pending</option>
              </select>
              <select
                value={sortOption}
                onChange={e => { setSortOption(e.target.value as SortOption); setPage(1); }}
                className="input w-auto"
              >
                <option value="sent_at_desc">Newest first</option>
                <option value="sent_at_asc">Oldest first</option>
                <option value="recipient_email_asc">Recipient A–Z</option>
              </select>
            </div>

            {historyError && (
              <div className="card p-6 text-center border-red-500/20 mb-4">
                <p className="text-sm text-red-400 mb-3">{historyError}</p>
                <button onClick={fetchHistory} className="btn-danger">Retry</button>
              </div>
            )}

            <div className="card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b border-zinc-800">
                    <tr>
                      <th className={thCls}>Recipient</th>
                      <th className={thCls}>Subject</th>
                      <th className={thCls}>Template</th>
                      <th className={thCls}>Campaign</th>
                      <th className={thCls}>Status</th>
                      <th className={thCls}>Sent at</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/60">
                    {historyLoading && [1, 2, 3].map(n => <SkeletonRow key={n} />)}
                    {!historyLoading && !historyError && history?.emails.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-4 py-16 text-center">
                          <div className="flex flex-col items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-zinc-800 border border-zinc-700 flex items-center justify-center">
                              <Clock className="w-5 h-5 text-zinc-600" />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-zinc-400">No emails sent yet</p>
                              <p className="text-xs text-zinc-600 mt-0.5">Start a mail merge to see history here</p>
                            </div>
                            <button onClick={() => navigate('/merge')} className="btn-primary text-xs px-3 py-2 mt-1">
                              Start mail merge
                            </button>
                          </div>
                        </td>
                      </tr>
                    )}
                    {!historyLoading && history?.emails.map(email => (
                      <tr key={email.id} className="hover:bg-zinc-800/30 transition-colors">
                        <td className={`${tdCls} text-zinc-300 max-w-[160px] truncate`} title={email.recipient_email}>{email.recipient_email}</td>
                        <td className={`${tdCls} text-zinc-400 max-w-[180px] truncate`} title={email.subject}>{email.subject}</td>
                        <td className={tdCls}><TemplateBadge name={email.template_name} /></td>
                        <td className={tdCls}><CampaignBadge name={email.campaign_name} /></td>
                        <td className={tdCls}><StatusBadge status={email.status} /></td>
                        <td className={`${tdCls} text-zinc-500 whitespace-nowrap text-xs`}>{formatDate(email.sent_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {history && history.total > 0 && (
                <div className="px-4 py-3 border-t border-zinc-800 flex items-center justify-between text-xs text-zinc-500">
                  <span>Showing {showingFrom}–{showingTo} of {history.total}</span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                      className="p-1.5 rounded-lg hover:bg-zinc-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <span>Page {history.page} of {history.total_pages}</span>
                    <button
                      onClick={() => setPage(p => Math.min(history.total_pages, p + 1))}
                      disabled={page === history.total_pages}
                      className="p-1.5 rounded-lg hover:bg-zinc-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── Grouped View Tab ──────────────────────────────────────────── */}
        {activeTab === 'grouped' && (
          <div>
            {/* Group-by pills */}
            <div className="flex items-center gap-2 mb-6">
              <span className="text-xs text-zinc-600 font-medium uppercase tracking-wide">Group by:</span>
              {(['campaign', 'template', 'status'] as GroupBy[]).map(opt => (
                <button
                  key={opt}
                  onClick={() => { setGroupBy(opt); setSelectedGroup(null); setGroupDetail(null); }}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors capitalize ${
                    groupBy === opt
                      ? 'bg-indigo-600 text-white'
                      : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200'
                  }`}
                >
                  {opt}
                </button>
              ))}
            </div>

            {groupsError && (
              <div className="card p-6 text-center border-red-500/20 mb-4">
                <p className="text-sm text-red-400 mb-3">{groupsError}</p>
                <button onClick={fetchGroups} className="btn-danger">Retry</button>
              </div>
            )}

            {!groupsError && (
              <div className="overflow-x-auto pb-2 mb-6">
                <div className="flex gap-3" style={{ minWidth: 'max-content' }}>
                  {groupsLoading && [1, 2, 3].map(n => (
                    <div key={n} className="w-52 card p-5 animate-pulse flex-shrink-0">
                      <div className="h-3 bg-zinc-800 rounded mb-3 w-3/4" />
                      <div className="h-8 bg-zinc-800 rounded mb-2 w-1/2" />
                      <div className="h-2.5 bg-zinc-800/60 rounded w-full" />
                    </div>
                  ))}
                  {!groupsLoading && groups.length === 0 && (
                    <div className="card p-8 text-center">
                      <p className="text-sm text-zinc-500">No email data to group yet.</p>
                    </div>
                  )}
                  {!groupsLoading && groups.map((group, idx) => (
                    <div
                      key={idx}
                      onClick={() => handleSelectGroup(group)}
                      className={`w-52 flex-shrink-0 card p-5 cursor-pointer hover:border-zinc-700 transition-all duration-150 ${
                        selectedGroup?.group_id === group.group_id && selectedGroup?.group_name === group.group_name
                          ? 'border-indigo-500/40 bg-indigo-500/5'
                          : ''
                      }`}
                    >
                      <h3 className="text-sm font-semibold text-zinc-200 mb-3 truncate" title={group.group_name}>{group.group_name}</h3>
                      <p className="text-2xl font-bold text-zinc-100 mb-0.5">{group.total}</p>
                      <p className="text-xs text-zinc-600 mb-3">total emails</p>
                      <div className="flex gap-3 text-xs">
                        <span className="text-emerald-400 font-medium">✓ {group.success_count}</span>
                        <span className="text-red-400 font-medium">✗ {group.error_count}</span>
                      </div>
                      <p className="text-xs text-zinc-700 mt-2">
                        {group.last_sent_at ? `Last: ${formatShortDate(group.last_sent_at)}` : 'No sends yet'}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Group detail */}
            {selectedGroup && (
              <div className="card overflow-hidden">
                <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800">
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-200">{selectedGroup.group_name}</h3>
                    <p className="text-xs text-zinc-500 mt-0.5">{selectedGroup.total} email{selectedGroup.total !== 1 ? 's' : ''}</p>
                  </div>
                  <button
                    onClick={() => { setSelectedGroup(null); setGroupDetail(null); }}
                    className="p-1.5 rounded-lg text-zinc-600 hover:text-zinc-300 hover:bg-zinc-800 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                {detailLoading && (
                  <div className="p-8 flex justify-center"><div className="spinner" /></div>
                )}
                {detailError && (
                  <div className="p-6 text-center text-sm text-red-400">{detailError}</div>
                )}
                {!detailLoading && !detailError && groupDetail && (
                  <>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="border-b border-zinc-800">
                          <tr>
                            <th className={thCls}>Recipient</th>
                            <th className={thCls}>Subject</th>
                            <th className={thCls}>Status</th>
                            <th className={thCls}>Sent at</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-zinc-800/60">
                          {groupDetail.emails.length === 0 && (
                            <tr>
                              <td colSpan={4} className="px-4 py-8 text-center text-sm text-zinc-500">No emails in this group.</td>
                            </tr>
                          )}
                          {groupDetail.emails.map(email => (
                            <tr key={email.id} className="hover:bg-zinc-800/30 transition-colors">
                              <td className={`${tdCls} text-zinc-300 max-w-[180px] truncate`} title={email.recipient_email}>{email.recipient_email}</td>
                              <td className={`${tdCls} text-zinc-400 max-w-[200px] truncate`} title={email.subject}>{email.subject}</td>
                              <td className={tdCls}><StatusBadge status={email.status} /></td>
                              <td className={`${tdCls} text-zinc-500 whitespace-nowrap text-xs`}>{formatDate(email.sent_at)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    {groupDetail.total_pages > 1 && (
                      <div className="px-4 py-3 border-t border-zinc-800 flex items-center justify-between text-xs text-zinc-500">
                        <span>Page {groupDetail.page} of {groupDetail.total_pages} ({groupDetail.total} total)</span>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleDetailPageChange(detailPage - 1)}
                            disabled={detailPage === 1}
                            className="p-1.5 rounded-lg hover:bg-zinc-800 disabled:opacity-30 transition-colors"
                          >
                            <ChevronLeft className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDetailPageChange(detailPage + 1)}
                            disabled={detailPage === groupDetail.total_pages}
                            className="p-1.5 rounded-lg hover:bg-zinc-800 disabled:opacity-30 transition-colors"
                          >
                            <ChevronRight className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
