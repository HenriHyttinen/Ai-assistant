// @ts-nocheck
import { useEffect, useState } from 'react';
import { 
  Box, Heading, Table, Thead, Tbody, Tr, Th, Td, Spinner, Text, Select, 
  HStack, Button, VStack, Card, CardBody, CardHeader, Badge, 
  Stat, StatLabel, StatNumber, StatHelpText, Grid, GridItem,
  Tabs, TabList, TabPanels, Tab, TabPanel, Divider, useToast,
  Menu, MenuButton, MenuList, MenuItem, useBreakpointValue
} from '@chakra-ui/react';
import { ChevronDownIcon, DownloadIcon } from '@chakra-ui/icons';
import { useApp } from '../contexts/AppContext';
import { analytics, exportService } from '../services/api';
import { t } from '../utils/translations';
import ExportModal from '../components/ExportModal';
import UniversalExportButton from '../components/UniversalExportButton';

interface ActivityLog {
  id: number;
  activity_type: string;
  duration: number;
  intensity?: string;
  notes?: string;
  performed_at?: string;
  created_at: string;
}

interface HealthSummary {
  period: {
    start: string;
    end: string;
    type: string;
  };
  metrics: {
    current_weight?: number;
    weight_change: number;
    current_bmi?: number;
    current_wellness_score?: number;
    wellness_score_change?: number;
  };
  activities: {
    total_duration: number;
    activity_count: number;
    average_duration: number;
    activity_types: string[];
    weekly_average?: number;
  };
  goals_progress?: {
    weight_goal: {
      target: number;
      current: number;
      progress_percentage: number;
    };
    activity_goal: {
      target_frequency: number;
      actual_frequency: number;
      progress_percentage: number;
    };
  };
}

const ActivityHistory = () => {
  const { language } = useApp();
  const toast = useToast();
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [weeklySummary, setWeeklySummary] = useState<HealthSummary | null>(null);
  const [monthlySummary, setMonthlySummary] = useState<HealthSummary | null>(null);
  const [days, setDays] = useState(30);
  const [sortOrder, setSortOrder] = useState('desc');
  const [loading, setLoading] = useState(true);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  
  // Mobile-responsive values
  const isMobile = useBreakpointValue({ base: true, md: false });

  const load = async () => {
    setLoading(true);
    try {
      const res = await analytics.getActivities(days, sortOrder);
      setLogs(res.data);
    } finally {
      setLoading(false);
    }
  };

  const loadSummaries = async () => {
    setSummaryLoading(true);
    try {
      const [weeklyRes, monthlyRes] = await Promise.all([
        analytics.getWeeklySummary(),
        analytics.getMonthlySummary()
      ]);
      setWeeklySummary(weeklyRes.data);
      setMonthlySummary(monthlyRes.data);
    } catch (error) {
      console.error('Error loading summaries:', error);
    } finally {
      setSummaryLoading(false);
    }
  };

  useEffect(() => { load(); }, [days, sortOrder]);
  useEffect(() => { loadSummaries(); }, []);

  const downloadFile = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExportActivities = async (format: string) => {
    try {
      setExportLoading(true);
      const response = await analytics.exportActivities(days, format);
      
      const filename = `activities_export_${new Date().toISOString().split('T')[0]}.${format}`;
      downloadFile(response.data, filename);
      
      toast({
        title: 'Export Successful',
        description: `Your activities have been exported as ${format?.toUpperCase() || 'FILE'}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error: any) {
      toast({
        title: 'Export Failed',
        description: error.response?.data?.detail || 'Failed to export activities',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setExportLoading(false);
    }
  };

  const handleExportAllData = async (format: string) => {
    try {
      setExportLoading(true);
      const response = await analytics.exportHealthData(format);
      
      const filename = `health_data_export_${new Date().toISOString().split('T')[0]}.${format}`;
      downloadFile(response.data, filename);
      
      toast({
        title: 'Export Successful',
        description: `Your complete health data has been exported as ${format?.toUpperCase() || 'FILE'}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error: any) {
      toast({
        title: 'Export Failed',
        description: error.response?.data?.detail || 'Failed to export health data',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setExportLoading(false);
    }
  };

  const handleExportWeeklySummary = async (format: string) => {
    try {
      setExportLoading(true);
      const response = await exportService.exportWeeklySummary(format);
      
      const filename = `weekly_summary_${new Date().toISOString().split('T')[0]}.${format}`;
      downloadFile(response.data, filename);
      
      toast({
        title: 'Export Successful',
        description: `Your weekly summary has been exported as ${format?.toUpperCase() || 'FILE'}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error: any) {
      toast({
        title: 'Export Failed',
        description: error.response?.data?.detail || 'Failed to export weekly summary',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setExportLoading(false);
    }
  };

  const handleExportMonthlySummary = async (format: string) => {
    try {
      setExportLoading(true);
      const response = await exportService.exportMonthlySummary(format);
      
      const filename = `monthly_summary_${new Date().toISOString().split('T')[0]}.${format}`;
      downloadFile(response.data, filename);
      
      toast({
        title: 'Export Successful',
        description: `Your monthly summary has been exported as ${format?.toUpperCase() || 'FILE'}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error: any) {
      toast({
        title: 'Export Failed',
        description: error.response?.data?.detail || 'Failed to export monthly summary',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setExportLoading(false);
    }
  };

  const formatDate = (iso: string) => new Date(iso).toLocaleString();
  const formatDateShort = (iso: string) => new Date(iso).toLocaleDateString();

  const renderSummaryCard = (summary: HealthSummary, title: string) => (
    <Card>
      <CardHeader>
        <Heading size="md">{title}</Heading>
        <Text fontSize="sm" color="gray.500">
          {formatDateShort(summary.period.start)} - {formatDateShort(summary.period.end)}
        </Text>
      </CardHeader>
      <CardBody>
        <Grid templateColumns="repeat(2, 1fr)" gap={4}>
          <Stat>
            <StatLabel>Total Activities</StatLabel>
            <StatNumber>{summary.activities.activity_count}</StatNumber>
            <StatHelpText>
              {summary.activities.weekly_average ? 
                `${summary.activities.weekly_average} min/week avg` : 
                `${summary.activities.average_duration} min avg`
              }
            </StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Total Duration</StatLabel>
            <StatNumber>{summary.activities.total_duration}</StatNumber>
            <StatHelpText>minutes</StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Weight Change</StatLabel>
            <StatNumber color={summary.metrics.weight_change > 0 ? 'green.500' : 'red.500'}>
              {summary.metrics.weight_change > 0 ? '+' : ''}{summary.metrics.weight_change.toFixed(1)} kg
            </StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Wellness Score</StatLabel>
            <StatNumber>{summary.metrics.current_wellness_score?.toFixed(1) || 'N/A'}</StatNumber>
            {summary.metrics.wellness_score_change && (
              <StatHelpText color={summary.metrics.wellness_score_change > 0 ? 'green.500' : 'red.500'}>
                {summary.metrics.wellness_score_change > 0 ? '+' : ''}{summary.metrics.wellness_score_change.toFixed(1)}
              </StatHelpText>
            )}
          </Stat>
        </Grid>
        
        {summary.activities.activity_types.length > 0 && (
          <Box mt={4}>
            <Text fontSize="sm" fontWeight="bold" mb={2}>Activity Types:</Text>
            <HStack spacing={2} flexWrap="wrap">
              {summary.activities.activity_types.map((type, index) => (
                <Badge key={index} colorScheme="blue" textTransform="capitalize">
                  {type.replace('_', ' ')}
                </Badge>
              ))}
            </HStack>
          </Box>
        )}

        {summary.goals_progress && (
          <Box mt={4}>
            <Text fontSize="sm" fontWeight="bold" mb={2}>Goal Progress:</Text>
            <VStack spacing={2} align="stretch">
              <Box>
                <Text fontSize="xs">Weight Goal: {summary.goals_progress.weight_goal.progress_percentage.toFixed(1)}%</Text>
                <Box bg="gray.200" h="4px" borderRadius="2px" overflow="hidden">
                  <Box 
                    bg="blue.500" 
                    h="100%" 
                    w={`${Math.min(100, Math.max(0, summary.goals_progress.weight_goal.progress_percentage))}%`}
                  />
                </Box>
              </Box>
              <Box>
                <Text fontSize="xs">Activity Goal: {summary.goals_progress.activity_goal.progress_percentage.toFixed(1)}%</Text>
                <Box bg="gray.200" h="4px" borderRadius="2px" overflow="hidden">
                  <Box 
                    bg="green.500" 
                    h="100%" 
                    w={`${Math.min(100, Math.max(0, summary.goals_progress.activity_goal.progress_percentage))}%`}
                  />
                </Box>
              </Box>
            </VStack>
          </Box>
        )}
      </CardBody>
    </Card>
  );

  return (
    <Box>
      <VStack spacing={4} align="stretch" mb={6}>
        <HStack justify="space-between" align="center">
          <Heading size={isMobile ? "md" : "lg"}>
            {t('activityTypes' as any, language)} {t('history' as any, language) || 'History'}
          </Heading>
        </HStack>
        <HStack spacing={isMobile ? 2 : 3} flexWrap="wrap" justify={isMobile ? "center" : "flex-end"}>
          <Select 
            value={days} 
            onChange={(e) => setDays(Number(e.target.value))} 
            width={isMobile ? "100px" : "120px"}
            size={isMobile ? "xs" : "sm"}
          >
            <option value={7}>{isMobile ? "7d" : "7 days"}</option>
            <option value={30}>{isMobile ? "30d" : "30 days"}</option>
            <option value={90}>{isMobile ? "90d" : "90 days"}</option>
          </Select>
          <Select 
            value={sortOrder} 
            onChange={(e) => setSortOrder(e.target.value)} 
            width={isMobile ? "100px" : "120px"}
            size={isMobile ? "xs" : "sm"}
          >
            <option value="desc">{isMobile ? "Newest" : "Newest First"}</option>
            <option value="asc">{isMobile ? "Oldest" : "Oldest First"}</option>
          </Select>
          <Button 
            onClick={load} 
            isLoading={loading} 
            size={isMobile ? "xs" : "sm"}
            minW={isMobile ? "60px" : "auto"}
          >
            {t('refresh' as any, language) || 'Refresh'}
          </Button>
                 <UniversalExportButton
                   onExportActivities={handleExportActivities}
                   onExportAllData={handleExportAllData}
                   onExportWeeklySummary={handleExportWeeklySummary}
                   onExportMonthlySummary={handleExportMonthlySummary}
                   isLoading={exportLoading}
                 />
        </HStack>
      </VStack>

      <Tabs>
        <TabList>
          <Tab>Activity History</Tab>
          <Tab>Weekly Summary</Tab>
          <Tab>Monthly Summary</Tab>
        </TabList>

        <TabPanels>
          <TabPanel px={0}>
            {loading ? (
              <Box textAlign="center" py={8}>
                <Spinner size="lg" />
                <Text mt={4}>Loading activities...</Text>
              </Box>
            ) : logs.length === 0 ? (
              <Text color="gray.500" textAlign="center" py={8}>
                {t('noneRecorded' as any, language) || 'No activities recorded'}
              </Text>
            ) : (
              <Table size="sm" variant="simple">
                <Thead>
                  <Tr>
                    <Th>{t('date' as any, language) || 'Date'}</Th>
                    <Th>{t('activityType' as any, language) || 'Activity Type'}</Th>
                    <Th isNumeric>{t('duration' as any, language) || 'Duration'}</Th>
                    <Th>{t('intensity' as any, language) || 'Intensity'}</Th>
                    <Th>{t('notes' as any, language) || 'Notes'}</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {logs.map((log) => (
                    <Tr key={log.id}>
                      <Td>{formatDate(log.performed_at || log.created_at)}</Td>
                      <Td textTransform="capitalize">{log.activity_type.replace('_',' ')}</Td>
                      <Td isNumeric>{log.duration} min</Td>
                      <Td>{log.intensity || '-'}</Td>
                      <Td>{log.notes || '-'}</Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            )}
          </TabPanel>

          <TabPanel px={0}>
            {summaryLoading ? (
              <Box textAlign="center" py={8}>
                <Spinner size="lg" />
                <Text mt={4}>Loading weekly summary...</Text>
              </Box>
            ) : weeklySummary ? (
              renderSummaryCard(weeklySummary, "Weekly Health Summary")
            ) : (
              <Text color="gray.500" textAlign="center" py={8}>
                No weekly summary available
              </Text>
            )}
          </TabPanel>

          <TabPanel px={0}>
            {summaryLoading ? (
              <Box textAlign="center" py={8}>
                <Spinner size="lg" />
                <Text mt={4}>Loading monthly summary...</Text>
              </Box>
            ) : monthlySummary ? (
              renderSummaryCard(monthlySummary, "Monthly Health Summary")
            ) : (
              <Text color="gray.500" textAlign="center" py={8}>
                No monthly summary available
              </Text>
            )}
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default ActivityHistory;