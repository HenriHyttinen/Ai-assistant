import React, { useState, useEffect } from 'react';
import {
  Select,
  FormControl,
  FormLabel,
  VStack,
  Text,
  HStack,
  Icon,
  Box
} from '@chakra-ui/react';
import { FiClock, FiGlobe } from 'react-icons/fi';

interface TimezoneSelectorProps {
  value: string;
  onChange: (timezone: string) => void;
  disabled?: boolean;
}

interface Timezone {
  value: string;
  label: string;
}

const TimezoneSelector: React.FC<TimezoneSelectorProps> = ({
  value,
  onChange,
  disabled = false
}) => {
  const [timezones, setTimezones] = useState<Timezone[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTimezones = async () => {
      try {
        const response = await fetch('http://localhost:8000/settings/timezones');
        if (response.ok) {
          const data = await response.json();
          setTimezones(data);
        } else {
          // Fallback timezones if API fails
          setTimezones([
            { value: 'UTC', label: 'UTC (Coordinated Universal Time)' },
            { value: 'America/New_York', label: 'Eastern Time (US & Canada)' },
            { value: 'America/Chicago', label: 'Central Time (US & Canada)' },
            { value: 'America/Denver', label: 'Mountain Time (US & Canada)' },
            { value: 'America/Los_Angeles', label: 'Pacific Time (US & Canada)' },
            { value: 'Europe/London', label: 'London (GMT/BST)' },
            { value: 'Europe/Paris', label: 'Paris (CET/CEST)' },
            { value: 'Europe/Berlin', label: 'Berlin (CET/CEST)' },
            { value: 'Asia/Tokyo', label: 'Tokyo (JST)' },
            { value: 'Asia/Shanghai', label: 'Shanghai (CST)' },
            { value: 'Australia/Sydney', label: 'Sydney (AEST/AEDT)' }
          ]);
        }
      } catch (error) {
        console.error('Error fetching timezones:', error);
        // Use fallback timezones
        setTimezones([
          { value: 'UTC', label: 'UTC (Coordinated Universal Time)' },
          { value: 'America/New_York', label: 'Eastern Time (US & Canada)' },
          { value: 'Europe/London', label: 'London (GMT/BST)' }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchTimezones();
  }, []);

  if (loading) {
    return (
      <FormControl>
        <FormLabel>Timezone</FormLabel>
        <Select placeholder="Loading timezones..." disabled />
      </FormControl>
    );
  }

  return (
    <VStack spacing={3} align="stretch">
      <FormControl>
        <FormLabel>
          <HStack>
            <Icon as={FiGlobe} />
            <Text>Timezone</Text>
          </HStack>
        </FormLabel>
        <Select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          placeholder="Select your timezone"
        >
          {timezones.map((tz) => (
            <option key={tz.value} value={tz.value}>
              {tz.label}
            </option>
          ))}
        </Select>
      </FormControl>
      
      <Box p={3} bg="gray.50" borderRadius="md">
        <HStack>
          <Icon as={FiClock} color="blue.500" />
          <VStack align="start" spacing={1}>
            <Text fontSize="sm" fontWeight="medium">
              Current Time in {timezones.find(tz => tz.value === value)?.label || 'Selected Timezone'}
            </Text>
            <Text fontSize="xs" color="gray.600">
              All dates and times will be displayed in your selected timezone
            </Text>
          </VStack>
        </HStack>
      </Box>
    </VStack>
  );
};

export default TimezoneSelector;










