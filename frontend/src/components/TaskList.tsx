import React, { useState, useEffect, useCallback } from 'react';
import { 
  Card, Table, Button, Space, Tag, Modal, Form, Input, Select, 
  Upload, Progress, message, Popconfirm, Typography, Empty, Spin 
} from 'antd';
import { 
  PlusOutlined, PlayCircleOutlined, PauseCircleOutlined, 
  DeleteOutlined, FolderOpenOutlined, InboxOutlined, ReloadOutlined 
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { api, Task, TranscodeSettings } from '../services/api';

const { Dragger } = Upload;
const { Text } = Typography;

const CODEC_OPTIONS = [
  { value: 'libx264', label: 'H.264 (推荐)' },
  { value: 'libx265', label: 'H.265/HEVC' },
  { value: 'libvpx-vp9', label: 'VP9' },
  { value: 'prores', label: 'ProRes' },
];

const RESOLUTION_OPTIONS = [
  { value: '1920x1080', label: '1080p (1920x1080)' },
  { value: '1280x720', label: '720p (1280x720)' },
  { value: '854x480', label: '480p (854x480)' },
  { value: '640x360', label: '360p (640x360)' },
];

const BITRATE_OPTIONS = [
  { value: '5000k', label: '5 Mbps' },
  { value: '3000k', label: '3 Mbps' },
  { value: '2000k', label: '2 Mbps' },
  { value: '1000k', label: '1 Mbps' },
  { value: '500k', label: '500 Kbps' },
];

const STATUS_COLORS: Record<string, string> = {
  pending: 'default',
  running: 'processing',
  completed: 'success',
  failed: 'error',
  cancelled: 'warning',
};

const STATUS_TEXT: Record<string, string> = {
  pending: '等待中',
  running: '转码中',
  completed: '已完成',
  failed: '失败',
  cancelled: '已取消',
};

export const TaskList: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [form] = Form.useForm();

  const fetchTasks = useCallback(async () => {
    try {
      const data = await api.listTasks();
      setTasks(data);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 2000);
    return () => clearInterval(interval);
  }, [fetchTasks]);

  const handleCreateTask = async (values: any) => {
    if (selectedFiles.length === 0) {
      message.error('请至少选择一个文件');
      return;
    }

    setUploading(true);
    try {
      const settings: TranscodeSettings = {
        codec: values.codec,
        resolution: values.resolution,
        video_bitrate: values.video_bitrate,
        audio_bitrate: values.audio_bitrate,
      };
      
      await api.createTask(selectedFiles, settings, values.name);
      message.success('任务创建成功');
      setCreateModalOpen(false);
      setSelectedFiles([]);
      form.resetFields();
      fetchTasks();
    } catch (error) {
      message.error('任务创建失败');
    } finally {
      setUploading(false);
    }
  };

  const handleStartTask = async (taskId: string) => {
    try {
      await api.startTask(taskId);
      message.success('任务已启动');
      fetchTasks();
    } catch (error) {
      message.error('启动失败');
    }
  };

  const handleCancelTask = async (taskId: string) => {
    try {
      await api.cancelTask(taskId);
      message.success('任务已取消');
      fetchTasks();
    } catch (error) {
      message.error('取消失败');
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await api.deleteTask(taskId);
      message.success('任务已删除');
      fetchTasks();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const columns: ColumnsType<Task> = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={STATUS_COLORS[status]}>{STATUS_TEXT[status]}</Tag>
      ),
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 200,
      render: (progress: number, record: Task) => (
        <Progress 
          percent={progress} 
          size="small"
          status={record.status === 'failed' ? 'exception' : record.status === 'completed' ? 'success' : 'active'}
        />
      ),
    },
    {
      title: '文件',
      key: 'files',
      width: 150,
      render: (_, record: Task) => (
        <Text>
          {record.completed_files}/{record.total_files} 完成
          {record.failed_files > 0 && (
            <Text type="danger"> ({record.failed_files} 失败)</Text>
          )}
        </Text>
      ),
    },
    {
      title: '当前文件',
      dataIndex: 'current_file',
      key: 'current_file',
      width: 200,
      ellipsis: true,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record: Task) => (
        <Space>
          {record.status === 'pending' && (
            <Button 
              type="link" 
              icon={<PlayCircleOutlined />} 
              onClick={() => handleStartTask(record.id)}
            >
              启动
            </Button>
          )}
          {record.status === 'running' && (
            <Button 
              type="link" 
              icon={<PauseCircleOutlined />} 
              onClick={() => handleCancelTask(record.id)}
            >
              暂停
            </Button>
          )}
          <Popconfirm
            title="确定删除此任务?"
            onConfirm={() => handleDeleteTask(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const uploadProps = {
    multiple: true,
    beforeUpload: (file: File) => {
      const videoExtensions = ['.mp4', '.mov', '.avi', '.mkv', '.m4v', '.mxf', '.webm', '.flv'];
      const ext = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      if (!videoExtensions.includes(ext)) {
        message.error(`${file.name} 不是视频文件`);
        return Upload.LIST_IGNORE;
      }
      setSelectedFiles(prev => [...prev, file]);
      return false;
    },
    fileList: selectedFiles.map((file, index) => ({
      uid: index.toString(),
      name: file.name,
      size: file.size,
      status: 'done' as const,
    })),
    onRemove: (file: any) => {
      setSelectedFiles(prev => prev.filter((_, i) => i.toString() !== file.uid));
    },
  };

  return (
    <Card 
      title="视频转码任务" 
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalOpen(true)}>
          创建任务
        </Button>
      }
    >
      <Table
        columns={columns}
        dataSource={tasks}
        rowKey="id"
        loading={loading}
        locale={{ emptyText: <Empty description="暂无任务" /> }}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title="创建转码任务"
        open={createModalOpen}
        onCancel={() => {
          setCreateModalOpen(false);
          setSelectedFiles([]);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleCreateTask}>
          <Form.Item label="任务名称" name="name">
            <Input placeholder="留空使用默认名称" />
          </Form.Item>

          <Form.Item label="转码设置" required>
            <Space style={{ width: '100%' }} direction="vertical">
              <Space>
                <Form.Item label="编码格式" name="codec" initialValue="libx264" noStyle>
                  <Select options={CODEC_OPTIONS} style={{ width: 150 }} />
                </Form.Item>
                <Form.Item label="分辨率" name="resolution" initialValue="1280x720" noStyle>
                  <Select options={RESOLUTION_OPTIONS} style={{ width: 150 }} />
                </Form.Item>
              </Space>
              <Space>
                <Form.Item label="视频码率" name="video_bitrate" initialValue="2000k" noStyle>
                  <Select options={BITRATE_OPTIONS} style={{ width: 150 }} />
                </Form.Item>
                <Form.Item label="音频码率" name="audio_bitrate" initialValue="128k" noStyle>
                  <Select 
                    options={[
                      { value: '192k', label: '192 Kbps' },
                      { value: '128k', label: '128 Kbps' },
                      { value: '96k', label: '96 Kbps' },
                      { value: '64k', label: '64 Kbps' },
                    ]} 
                    style={{ width: 150 }} 
                  />
                </Form.Item>
              </Space>
            </Space>
          </Form.Item>

          <Form.Item label="选择视频文件" required>
            <Dragger {...uploadProps}>
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p className="ant-upload-hint">
                支持 MP4, MOV, AVI, MKV, M4V, MXF, WebM 等格式
              </p>
            </Dragger>
            {selectedFiles.length > 0 && (
              <div style={{ marginTop: 8 }}>
                已选择 {selectedFiles.length} 个文件
              </div>
            )}
          </Form.Item>

          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => setCreateModalOpen(false)}>取消</Button>
              <Button type="primary" htmlType="submit" loading={uploading}>
                创建任务
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};
