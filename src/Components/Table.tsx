import React from 'react';
import { Table, Input, Button, Space } from 'antd';
import { DownloadOutlined, SearchOutlined } from '@ant-design/icons';
import type { TableProps } from 'antd';

interface SmartTableProps extends Omit<TableProps<any>, 'title'> {
    title?: string;
    exportButtons?: boolean;
    searchable?: boolean;
}

const SmartTable: React.FC<SmartTableProps> = ({
    title,
    exportButtons = true,
    searchable = true,
    columns,
    dataSource,
    ...rest
}) => {
    return (
        <div style={{ background: '#fff', borderRadius: 8, padding: 16, marginBottom: 24 }}>
            {title && (
                <h3 style={{ color: '#00b39f', marginBottom: 16 }}>{title}</h3>
            )}
            <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }} wrap>

                {searchable && (
                    <Input
                        placeholder="Search..."
                        prefix={<SearchOutlined />}
                        style={{ width: 250 }}
                        allowClear
                        onChange={(e) => {
                            // optional: implement filtering here
                        }}
                    />
                )}
            </Space>
            <Space style={{ marginBottom: 16 }}>
                {exportButtons && <><Button>Excel</Button> <Button>CSV</Button></>}
            </Space>

            <Table
                bordered
                columns={columns}
                dataSource={dataSource}
                scroll={{ x: true }}
                pagination={{ pageSize: 5 }}
                {...rest}
            />
        </div>
    );
};

export default SmartTable;
