import React, { useEffect, useState } from "react";
import { Table, Input, Button, Space, Select } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
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
    columns = [],
    dataSource = [],
    ...rest
}) => {

    const [filters, setFilters] = useState<any>({});
    const [filteredData, setFilteredData] = useState<any[]>([...(dataSource || [])]);
    const [searchText, setSearchText] = useState("");

    useEffect(() => {
        setFilteredData([...(dataSource || [])]);
    }, [dataSource]);
    useEffect(() => {

        let tempData = [...(dataSource || [])];

        // Global Search
        if (searchText) {
            tempData = tempData.filter((row: any) =>
                Object.values(row).some((value) =>
                    String(value ?? "")
                        .toLowerCase()
                        .includes(searchText.toLowerCase())
                )
            );
        }

        // Column Filters
        Object.keys(filters).forEach((k) => {
            if (filters[k] !== undefined && filters[k] !== "") {
                tempData = tempData.filter((row: any) =>
                    String(row[k] ?? "")
                        .toLowerCase()
                        .includes(filters[k].toLowerCase())
                );
            }
        });

        setFilteredData(tempData);

    }, [dataSource, filters, searchText]);
    const handleColumnFilter = (value: string, key: string) => {

        const newFilters = { ...filters, [key]: value }
        setFilters(newFilters)

        let tempData = [...(dataSource || [])]
        Object.keys(newFilters).forEach((k) => {
            if (newFilters[k]) {
                tempData = tempData.filter((row: any) =>
                    String(row[k] ?? "")
                        .toLowerCase()
                        .includes(newFilters[k].toLowerCase())
                )
            }
        })

        setFilteredData(tempData)
    }

    const leafColumns = (columns as any[]).flatMap((col: any) =>
        col.children ? col.children : [col]
    )

    const filterRow = (
        <tr>
            {leafColumns.map((col: any) => (
                <th key={col.dataIndex}>
                    <Select
                        allowClear
                        size="small"
                        style={{ width: "100%" }}
                        value={filters[col.dataIndex]}
                        onChange={(v) => handleColumnFilter(v || "", col.dataIndex)}
                    />
                </th>
            ))}
        </tr>
    )

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
                        value={searchText}
                        onChange={(e) => setSearchText(e.target.value)}
                    />
                )}

            </Space>

            <Space style={{ marginBottom: 16 }}>
                {exportButtons && <>
                    <Button>Excel</Button>
                    <Button>CSV</Button>
                </>}
            </Space>

            <Table
                rowKey="tradingAcc"
                bordered
                columns={columns}
                dataSource={filteredData}
                scroll={{ x: "max-content" }}
                pagination={false}
                components={{
                    header: {
                        wrapper: (props: any) => (
                            <thead {...props}>
                                {props.children}
                                {filterRow}
                            </thead>
                        ),
                    },
                }}
                {...rest}
            />

        </div>
    );
};

export default SmartTable;