/**
 * Unit conversion utilities for measurement system preferences
 */

export interface MeasurementSystem {
  measurementSystem: 'metric' | 'imperial';
}

/**
 * Convert weight from kg to display units based on user preference
 */
export function convertWeightForDisplay(weightKg: number, measurementSystem: 'metric' | 'imperial'): number {
  if (measurementSystem === 'imperial') {
    // Convert kg to pounds (1 kg = 2.20462 lbs)
    return Math.round(weightKg * 2.20462 * 10) / 10; // Round to 1 decimal place
  }
  return Math.round(weightKg * 10) / 10; // Round to 1 decimal place
}

/**
 * Convert weight from display units to kg for backend storage
 */
export function convertWeightToKg(weight: number, measurementSystem: 'metric' | 'imperial'): number {
  if (measurementSystem === 'imperial') {
    // Convert pounds to kg (1 lb = 0.453592 kg)
    return Math.round(weight * 0.453592 * 100) / 100; // Round to 2 decimal places
  }
  return Math.round(weight * 100) / 100; // Round to 2 decimal places
}

/**
 * Convert height from cm to display units based on user preference
 */
export function convertHeightForDisplay(heightCm: number, measurementSystem: 'metric' | 'imperial'): number {
  if (measurementSystem === 'imperial') {
    // Convert cm to inches (1 cm = 0.393701 inches)
    return Math.round(heightCm * 0.393701 * 10) / 10; // Round to 1 decimal place
  }
  return Math.round(heightCm * 10) / 10; // Round to 1 decimal place
}

/**
 * Convert height from display units to cm for backend storage
 */
export function convertHeightToCm(height: number, measurementSystem: 'metric' | 'imperial'): number {
  if (measurementSystem === 'imperial') {
    // Convert inches to cm (1 inch = 2.54 cm)
    return Math.round(height * 2.54 * 100) / 100; // Round to 2 decimal places
  }
  return Math.round(height * 100) / 100; // Round to 2 decimal places
}

/**
 * Get the appropriate unit label for weight based on measurement system
 */
export function getWeightUnit(measurementSystem: 'metric' | 'imperial'): string {
  return measurementSystem === 'imperial' ? 'lbs' : 'kg';
}

/**
 * Get the appropriate unit label for height based on measurement system
 */
export function getHeightUnit(measurementSystem: 'metric' | 'imperial'): string {
  return measurementSystem === 'imperial' ? 'in' : 'cm';
}

/**
 * Get the appropriate unit label for target weight based on measurement system
 */
export function getTargetWeightUnit(measurementSystem: 'metric' | 'imperial'): string {
  return measurementSystem === 'imperial' ? 'lbs' : 'kg';
}
