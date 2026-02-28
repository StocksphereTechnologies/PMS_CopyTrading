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

const License: React.FC = () => {
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
    { title: 'Expiry', dataIndex: 'expiry', sorter: (a: any, b: any) => a.expiry.localeCompare(b.expiry) },
    { title: 'Live', dataIndex: 'live', sorter: (a: any, b: any) => a.live.localeCompare(b.live) },
    { title: 'Pseudo Acc.', dataIndex: 'pseudoacc', sorter: (a: any, b: any) => a.pseudoacc - b.pseudoacc },
    { title: 'Broker', dataIndex: 'broker', sorter: (a: any, b: any) => a.broker - b.broker},
    { title: 'Comments', dataIndex: 'comments', sorter: (a: any, b: any) => a.comments.localeCompare(b.commments) },
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

export default License;
