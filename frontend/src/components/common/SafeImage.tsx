import React, { useState } from 'react';
import { Image } from '@chakra-ui/react';
import PlaceholderImage from './PlaceholderImage';

interface SafeImageProps {
  src?: string;
  alt?: string;
  height?: string | number;
  width?: string | number;
  borderRadius?: string;
  objectFit?: string;
  fallbackText?: string;
  fallbackIcon?: React.ElementType;
  [key: string]: any; // Allow other props to be passed through
}

const SafeImage: React.FC<SafeImageProps> = ({
  src,
  alt,
  fallbackText = 'Image',
  fallbackIcon,
  ...props
}) => {
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // List of known problematic domains that often fail
  const problematicDomains = [
    'ukcdn.ar-cdn.com',
    'eatwell101.club',
    'recipedbuploads.alaskaseafood.org',
    'theomnomnomicon.com',
    'assets.kraftfoods.com',
    'sparkpeo.hs.llnwd.net',
    'i.hungrygowhere.com',
    'kindredkitchen.ca',
    'www.recipegoulash.com',
    'www.cooklikeanasianmomma.com',
    'mealplannerpro.com',
    'ocmomblog.com',
    'simplegoodandtasty.com',
    'i.ytimg.com',
    'thumbor.thedailymeal.com'
  ];

  // Function to validate if URL is safe to load
  const isSafeUrl = (url: string): boolean => {
    if (!url || (!url.startsWith('http') && !url.startsWith('/'))) {
      return false;
    }
    
    // Check if URL is from a known problematic domain
    const isProblematicDomain = problematicDomains.some(domain => url.includes(domain));
    if (isProblematicDomain) {
      return false;
    }
    
    // Additional validation for common problematic patterns
    if (url.includes('cdn') && (url.includes('ar-cdn') || url.includes('llnwd'))) {
      return false;
    }
    
    // Block common problematic patterns
    if (url.includes('hungrygowhere.com') || 
        url.includes('kindredkitchen.ca') || 
        url.includes('recipegoulash.com') ||
        url.includes('ocmomblog.com') ||
        url.includes('simplegoodandtasty.com') ||
        url.includes('ytimg.com') ||
        url.includes('thedailymeal.com') ||
        url.includes('recipe') && url.includes('goulash')) {
      return false;
    }
    
    return true;
  };

  // Don't attempt to load if URL is not safe
  if (!isSafeUrl(src)) {
    return (
      <PlaceholderImage
        height={props.height || '150px'}
        text={fallbackText}
        icon={fallbackIcon}
      />
    );
  }

  if (hasError) {
    return (
      <PlaceholderImage
        height={props.height || '150px'}
        text={fallbackText}
        icon={fallbackIcon}
      />
    );
  }

  return (
    <Image
      src={src}
      alt={alt}
      onError={() => {
        setHasError(true);
        setIsLoading(false);
      }}
      onLoad={() => {
        setIsLoading(false);
      }}
      {...props}
    />
  );
};

export default SafeImage;
