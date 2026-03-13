import React, { useEffect, useState } from 'react'
import { summaryService } from '../../../Services/summaryService'

import SummaryTable from './SummaryTable'
import SymbolLevelSummary from './SymbolLevelSummary'
import PositionAnalyticsSummary from './PositionAnalyticsSummary'
import OrdersAnalyticsSummary from './OrderAnalytics'
import MarginsAnalytics from './MarginAnalytics'

const Summary = () => {

  const [data, setData] = useState<any>(null)
  const [updateTime, setUpdateTime] = useState("")

  useEffect(() => {

    const fetchSummary = async () => {
      try {
        const result = await summaryService.getSummary()
        setData(result)
      } catch (err) {
        console.error("Summary API error", err)
      }
    }
    fetchSummary()
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setUpdateTime(new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }))
    }, 1000)

    return () => clearInterval(interval)

  }, [])

  if (!data) {
    return (
      <div>

        <SummaryTable data={[]} />

        <SymbolLevelSummary data={[]} />

        <PositionAnalyticsSummary
          title="Positions Analytics [NET]"
          data={{ m2m: 0, pnl: 0, atPnl: 0, total: 0, open: 0, closed: 0 }}
          updateTime={updateTime}
        />

        <PositionAnalyticsSummary
          title="Positions Analytics [DAY]"
          data={{ m2m: 0, pnl: 0, atPnl: 0, total: 0, open: 0, closed: 0 }}
          updateTime={updateTime}
        />

        <OrdersAnalyticsSummary
          data={{ total: 0, open: 0, complete: 0, trigPend: 0, cancelled: 0, rejected: 0 }}
          updateTime={updateTime}
        />

        <MarginsAnalytics
          data={{ total: 0, utilized: 0, available: 0 }}
          updateTime={updateTime}
        />

      </div>
    )
  }
  
  return (

    <div>

      <SummaryTable data={data.account_summary} />

      <SymbolLevelSummary data={data.symbol_summary} />

      <PositionAnalyticsSummary
        title="Positions Analytics [NET]"
        data={data.positions_analytics}
        updateTime={updateTime}
      />

      <PositionAnalyticsSummary
        title="Positions Analytics [DAY]"
        data={data?.positions_day_analytics || { m2m: 0, pnl: 0, atPnl: 0, total: 0, open: 0, closed: 0 }}
        updateTime={updateTime}
      />
      <OrdersAnalyticsSummary
        data={data.orders_analytics}
        updateTime={updateTime}
      />

      <MarginsAnalytics
        data={data.margin_analytics}
        updateTime={updateTime}
      />

    </div>

  )

}

export default Summary