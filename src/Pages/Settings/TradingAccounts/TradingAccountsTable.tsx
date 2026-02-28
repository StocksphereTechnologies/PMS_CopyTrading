import React, { useEffect } from 'react';
import { Table, Button, message, Popconfirm, Tag } from 'antd';
import { EditOutlined, DeleteOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { accountService } from '../../../Services/accountService';
import { useAccountStore } from '../../../store/accountStore';
import type { ColumnsType } from 'antd/es/table';

interface AccountTableData {
  key: number;
  account_id: number;
  loginId: string;
  nickname: string;
  broker: string;
  live: string;
  session: string;
  paid: string;
  validated: string;
  created_at: string;
}

const TradingAccountsTable: React.FC<{ searchText: string }> = ({ searchText }) => {
  const { accounts, loading, setAccounts, setLoading, removeAccount } = useAccountStore();

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    setLoading(true);
    try {
      const response = await accountService.getAll();
      // Backend returns a List[AccountResponse], not { accounts: [] }
      setAccounts(Array.isArray(response) ? response : []);
    } catch (error: any) {
      console.error('Failed to fetch accounts:', error);
      message.error('Failed to fetch accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (accountId: number) => {
    try {
      await accountService.delete(accountId);
      removeAccount(accountId);
      message.success('Account deleted successfully');
    } catch (error: any) {
      message.error('Failed to delete account');
    }
  };

  const handleAuthorize = async (accountId: number) => {
    try {
      const response = await accountService.getZerodhaLoginUrl(accountId);
      window.open(response.login_url, '_blank', 'width=600,height=600');
    } catch (error: any) {
      message.error('Failed to get authorization URL');
    }
  };

  const columns: ColumnsType<AccountTableData> = [
    {
      title: 'Login Id',
      dataIndex: 'loginId',
      key: 'loginId',
      sorter: (a, b) => a.loginId.localeCompare(b.loginId),
      // Filtering is now handled by `filteredAccounts` before passing to Table
    },
    {
      title: 'Nickname',
      dataIndex: 'nickname',
      key: 'nickname',
      sorter: (a, b) => a.nickname.localeCompare(b.nickname),
    },
    {
      title: 'Broker',
      dataIndex: 'broker',
      key: 'broker',
      sorter: (a, b) => a.broker.localeCompare(b.broker),
    },
    {
      title: 'Live',
      dataIndex: 'live',
      key: 'live',
      render: (live: string) => (
        <Tag color={live === 'Yes' ? 'green' : 'orange'}>
          {live === 'Yes' ? <CheckCircleOutlined /> : <CloseCircleOutlined />} {live}
        </Tag>
      ),
      sorter: (a, b) => a.live.localeCompare(b.live),
    },
    {
      title: 'Session',
      dataIndex: 'session',
      key: 'session',
      render: (session: string) => (
        <Tag color={session === 'Valid' ? 'green' : 'red'}>
          {session}
        </Tag>
      ),
      sorter: (a, b) => a.session.localeCompare(b.session),
    },
    {
      title: 'Paid',
      dataIndex: 'paid',
      key: 'paid',
      render: (paid: string) => (
        <Tag color={paid === 'Yes' ? 'green' : 'red'}>
          {paid}
        </Tag>
      ),
      sorter: (a, b) => a.paid.localeCompare(b.paid),
    },
    {
      title: 'Validated',
      dataIndex: 'validated',
      key: 'validated',
      render: (validated: string) => (
        <Tag color={validated === 'Yes' ? 'green' : 'red'}>
          {validated}
        </Tag>
      ),
      sorter: (a, b) => a.validated.localeCompare(b.validated),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <div style={{ display: 'flex', gap: 8 }}>
          <Button
            icon={<EditOutlined />}
            size="small"
            type="primary"
            style={{ background: '#1890ff' }}
          >
            Edit
          </Button>
          {record.broker === 'ZERODHA' && (
            <Button
              icon={<CheckCircleOutlined />}
              size="small"
              onClick={() => handleAuthorize(record.account_id)}
              style={{ background: '#52c41a', color: '#fff', borderColor: '#52c41a' }}
            >
              Authorize
            </Button>
          )}
          <Popconfirm
            title="Are you sure you want to delete this account?"
            onConfirm={() => handleDelete(record.account_id)}
            okText="Yes"
            cancelText="No"
            okButtonProps={{ danger: true }}
          >
            <Button 
              icon={<DeleteOutlined />} 
              size="small" 
              danger
            >
              Delete
            </Button>
          </Popconfirm>
        </div>
      ),
    },
  ];

  // Transform accounts to table data
  const tableData: AccountTableData[] = accounts.map((account) => ({
    key: account.account_id,
    account_id: account.account_id,
    loginId: account.trading_login_id,
    nickname: account.nickname || 'N/A',
    broker: account.broker_name,
    live: account.is_enabled ? 'Yes' : 'No',
    session: account.is_validated ? 'Valid' : 'Invalid',
    paid: account.is_paid ? 'Yes' : 'No',
    validated: account.is_validated ? 'Yes' : 'No',
    created_at: account.created_at,
  }));

  return (
    <Table
      bordered
      pagination={{ pageSize: 10, showSizeChanger: true, showTotal: (total) => `Total ${total} accounts` }}
      columns={columns}
      dataSource={tableData}
      loading={loading}
      scroll={{ x: 'max-content' }}
      locale={{ emptyText: 'No accounts found. Create your first trading account!' }}
      style={{ width: '100%' }}
    />
  );
};

export default TradingAccountsTable;

