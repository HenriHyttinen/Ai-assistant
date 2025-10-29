import React from 'react';
import { Box, Icon, Text } from '@chakra-ui/react';
import { FiImage } from 'react-icons/fi';

interface PlaceholderImageProps {
  width?: string | number;
  height?: string | number;
  borderRadius?: string;
  bg?: string;
  icon?: React.ElementType;
  text?: string;
}

const PlaceholderImage: React.FC<PlaceholderImageProps> = ({
  width = '100%',
  height = '150px',
  borderRadius = 'md',
  bg = 'gray.100',
  icon: IconComponent = FiImage,
  text
}) => {
  return (
    <Box
      width={width}
      height={height}
      bg={bg}
      borderRadius={borderRadius}
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      border="1px solid"
      borderColor="gray.200"
    >
      <Icon as={IconComponent} boxSize={8} color="gray.400" mb={2} />
      {text && (
        <Text fontSize="sm" color="gray.500" textAlign="center">
          {text}
        </Text>
      )}
    </Box>
  );
};

export default PlaceholderImage;


