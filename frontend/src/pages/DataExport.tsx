// @ts-nocheck
import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  VStack,
  HStack,
  Select,
  useToast,
  Alert,
  AlertIcon,
  Spinner,
  Divider,
} from '@chakra-ui/react';
import { useState } from 'react';
import { exportService } from '../services/api';

const DataExport = () => {
  const [loading, setLoading] = useState(false);
  const [exportFormat, setExportFormat] = useState('json');
  const toast = useToast();

  const handleExportAllData = async () => {
    try {
      setLoading(true);
      const response = await exportService.exportHealthData(exportFormat);
      
      if (exportFormat === 'json') {
        // Download JSON file
        const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `health_data_export_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        // CSV download is handled by the backend
        const blob = new Blob([response.data], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `health_data_export_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
      
      toast({
        title: 'Export Successful',
        description: 'Your health data has been exported successfully.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error: any) {
      toast({
        title: 'Export Failed',
        description: error.response?.data?.detail || 'Failed to export data',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExportMetrics = async () => {
    try {
      setLoading(true);
      const response = await exportService.exportMetricsHistory(30, exportFormat);
      
      if (exportFormat === 'json') {
        const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `metrics_history_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        const blob = new Blob([response.data], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `metrics_history_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
      
      toast({
        title: 'Export Successful',
        description: 'Your metrics history has been exported successfully.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error: any) {
      toast({
        title: 'Export Failed',
        description: error.response?.data?.detail || 'Failed to export metrics history',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={4}>
      <Heading mb={6}>Data Export</Heading>
      
      <VStack spacing={6} align="stretch">
        <Alert status="info">
          <AlertIcon />
          <Text fontSize="sm">
            Want to take your health data with you? Export everything in JSON or CSV format. 
            Includes your profile, progress history, activities, and privacy settings.
          </Text>
        </Alert>

        <Card>
          <CardHeader>
            <Heading size="md">Export Format</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Text fontSize="sm" color="gray.600">
                Choose the format for your exported data:
              </Text>
              <Select
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value)}
                maxW="200px"
              >
                <option value="json">JSON</option>
                <option value="csv">CSV</option>
              </Select>
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Complete Health Data Export</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Text fontSize="sm" color="gray.600">
                Export all your health data including:
              </Text>
              <VStack spacing={2} align="start" fontSize="sm">
                <Text>• Personal health profile</Text>
                <Text>• Historical metrics (weight, BMI, wellness scores)</Text>
                <Text>• Activity logs and exercise records</Text>
                <Text>• Consent preferences and privacy settings</Text>
                <Text>• Account information and timestamps</Text>
              </VStack>
              <Button
                colorScheme="blue"
                onClick={handleExportAllData}
                isLoading={loading}
                loadingText="Exporting..."
                isDisabled={loading}
              >
                Export All Health Data
              </Button>
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Metrics History Export</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Text fontSize="sm" color="gray.600">
                Export your metrics history for the last 30 days:
              </Text>
              <VStack spacing={2} align="start" fontSize="sm">
                <Text>• Weight tracking over time</Text>
                <Text>• BMI calculations and trends</Text>
                <Text>• Wellness score progression</Text>
                <Text>• Timestamps for each measurement</Text>
              </VStack>
              <Button
                colorScheme="green"
                onClick={handleExportMetrics}
                isLoading={loading}
                loadingText="Exporting..."
                isDisabled={loading}
              >
                Export Metrics History
              </Button>
            </VStack>
          </CardBody>
        </Card>

        <Alert status="warning" size="sm">
          <AlertIcon />
          <Text fontSize="xs">
            <strong>Privacy Note:</strong> Your exported data contains personal health information. 
            Please store it securely and only share it with trusted healthcare providers.
          </Text>
        </Alert>
      </VStack>
    </Box>
  );
};

export default DataExport;
