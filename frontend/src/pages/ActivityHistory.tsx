// @ts-nocheck
import { useEffect, useState } from 'react';
import { Box, Heading, Table, Thead, Tbody, Tr, Th, Td, Spinner, Text, Select, HStack, Button } from '@chakra-ui/react';
import { useApp } from '../contexts/AppContext';
import { analytics } from '../services/api';
import { t } from '../utils/translations';

interface ActivityLog {
  id: number;
  activity_type: string;
  duration: number;
  intensity?: string;
  notes?: string;
  created_at: string;
}

const ActivityHistory = () => {
  const { language } = useApp();
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const res = await analytics.getActivities(days);
      setLogs(res.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [days]);

  const formatDate = (iso: string) => new Date(iso).toLocaleString();

  return (
    <Box>
      <HStack justify="space-between" mb={4}>
        <Heading size="lg">{t('activityTypes' as any, language)} {t('history' as any, language) || 'History'}</Heading>
        <HStack>
          <Select value={days} onChange={(e) => setDays(Number(e.target.value))} width="auto">
            <option value={7}>7d</option>
            <option value={30}>30d</option>
            <option value={90}>90d</option>
          </Select>
          <Button onClick={load} isLoading={loading}>{t('refresh' as any, language)}</Button>
        </HStack>
      </HStack>

      {loading ? (
        <Box textAlign="center" py={8}><Spinner size="lg" /><Text mt={2}>{t('loading' as any, language)}</Text></Box>
      ) : logs.length === 0 ? (
        <Text color="gray.500">{t('noneRecorded' as any, language)}</Text>
      ) : (
        <Table size="sm" variant="simple">
          <Thead>
            <Tr>
              <Th>{t('date' as any, language)}</Th>
              <Th>{t('activityType' as any, language)}</Th>
              <Th isNumeric>{t('duration' as any, language)}</Th>
              <Th>{t('intensity' as any, language)}</Th>
              <Th>{t('notes' as any, language)}</Th>
            </Tr>
          </Thead>
          <Tbody>
            {logs.map((log) => (
              <Tr key={log.id}>
                <Td>{formatDate(log.created_at)}</Td>
                <Td textTransform="capitalize">{log.activity_type.replace('_',' ')}</Td>
                <Td isNumeric>{log.duration} min</Td>
                <Td>{log.intensity || '-'}</Td>
                <Td>{log.notes || '-'}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      )}
    </Box>
  );
};

export default ActivityHistory;


