import React, { useState } from 'react';
import {
  Table,
  Input,
  Button,
  Row,
  Col,
  Space,
  Card
} from 'antd';
import { SearchOutlined } from '@ant-design/icons';

const History: React.FC = () => {
  const initialData: any[] = [];

  const [data] = useState(initialData);
  const [searchText, setSearchText] = useState('');
  const [filteredData, setFilteredData] = useState(initialData);
  const [filters, setFilters] = useState<{ [key: string]: string }>({});

  const handleSearch = (value: string) => {
    const lower = value.toLowerCase();
    setSearchText(value);
    if (value.trim() === '') {
      setFilteredData(initialData);
    } else {
      const filtered = initialData.filter((item) =>
        Object.values(item).some((val) =>
          String(val).toLowerCase().includes(lower)
        )
      );
      setFilteredData(filtered);
    }
  };

  const columns = [
    { title: 'Id', dataIndex: 'id', sorter: (a: any, b: any) => a.id.localeCompare(b.id) },
    { title: 'Date', dataIndex: 'date', sorter: (a: any, b: any) => a.date.localeCompare(b.date) },
    { title: 'Category', dataIndex: 'category', sorter: (a: any, b: any) => a.category.localeCompare(b.category) },
    { title: 'Type', dataIndex: 'type', sorter: (a: any, b: any) => a.type - b.type },
    { title: 'Amount', dataIndex: 'amount', sorter: (a: any, b: any) => a.amount - b.amount },
    { title: 'Bal. Before', dataIndex: 'balbefore', sorter: (a: any, b: any) => a.balbefore.localeCompare(b.balbefore) },
    { title: 'Bal. After', dataIndex: 'balafter', sorter: (a: any, b: any) => a.balafter.localeCompare(b.balafter) },
    { title: 'Remark', dataIndex: 'remark', sorter: (a: any, b: any) => a.remark.localeCompare(b.remark) },
  ];

  return (
    <div style={{ background: '#f6f8fb', minHeight: '100vh', padding: 24 }}>
      <Card
        style={{
          border: '1px solid #e6ebf1',
          borderRadius: 8,
          background: '#ffffff',
          maxWidth: 1600,
          margin: '0 auto',
        }}
        bodyStyle={{ padding: 24 }}
      >
        {/* Top actions */}
        <Row
          justify="space-between"
          style={{ marginBottom: 16, flexWrap: 'wrap' }}
          gutter={[8, 8]}
        >
          <Col xs={24} sm={12} md={12} lg={8}>
            <Space>
              <Button style={{ fontWeight: 'bold', backgroundColor: '#36454F', color: '#fff' }}>
                Excel
              </Button>
              <Button style={{ fontWeight: 'bold', backgroundColor: '#36454F', color: '#fff' }}>
                CSV
              </Button>
            </Space>
          </Col>
          <Col>
            <Input
              placeholder="Search"
              prefix={<SearchOutlined />}
              style={{ width: 200 }}
              value={searchText}
              onChange={(e) => handleSearch(e.target.value)}
            />
          </Col>
        </Row>

        {/* Ledger Table */}
        <Table
          columns={columns}
          dataSource={filteredData}
          pagination={false}
          bordered
          scroll={{ x: 'max-content' }}
          locale={{
            emptyText: (
              <div
                style={{
                  textAlign: 'center',
                  fontWeight: 'bold',
                  color: '#3d3d3d',
                }}
              >
                No data available in table
              </div>
            ),
          }}
        />
      </Card>
    </div>
  );
};

export default History;
