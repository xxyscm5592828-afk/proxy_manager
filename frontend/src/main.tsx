import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider, Layout, Typography } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { TaskList } from './components/TaskList'
import './index.css'

const { Header, Content } = Layout
const { Title } = Typography

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider locale={zhCN}>
      <Layout className="layout">
        <Header style={{ display: 'flex', alignItems: 'center' }}>
          <Title level={3} style={{ color: 'white', margin: 0 }}>
            视频转码管理器
          </Title>
        </Header>
        <Content style={{ padding: '24px', minHeight: 'calc(100vh - 64px)' }}>
          <TaskList />
        </Content>
      </Layout>
    </ConfigProvider>
  </React.StrictMode>,
)
