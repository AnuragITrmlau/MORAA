// ============================================================
// errors.ts — Custom Error Classes
// MORAA GemVision
// ============================================================

/**
 * Base application error with an error code and retryability flag.
 */
export class AppError extends Error {
  public readonly code: string;
  public readonly retryable: boolean;
  public readonly statusCode: number;

  constructor(
    message: string,
    code: string = "INTERNAL_ERROR",
    retryable: boolean = false,
    statusCode: number = 500
  ) {
    super(message);
    this.name = "AppError";
    this.code = code;
    this.retryable = retryable;
    this.statusCode = statusCode;
  }
}

/**
 * Errors originating from the Groq API.
 * Named GroqError — replaces the previous GeminiError.
 */
export class GroqError extends AppError {
  constructor(
    message: string,
    code: string = "GROQ_API_ERROR",
    retryable: boolean = false,
    statusCode: number = 502
  ) {
    super(message, code, retryable, statusCode);
    this.name = "GroqError";
  }
}

/**
 * Alias for backward compatibility — GeminiError now points to GroqError.
 */
export class GeminiError extends GroqError {
  constructor(
    message: string,
    code: string = "GEMINI_API_ERROR",
    retryable: boolean = false,
    statusCode: number = 502
  ) {
    super(message, code, retryable, statusCode);
    this.name = "GeminiError";
  }
}

/**
 * Quota exceeded — typically non-retryable until reset.
 */
export class QuotaExceededError extends GroqError {
  constructor(message: string = "API quota exceeded. Please try again later.") {
    super(message, "QUOTA_EXCEEDED", false, 429);
    this.name = "QuotaExceededError";
  }
}

/**
 * Content blocked by safety filters.
 */
export class SafetyBlockedError extends GroqError {
  constructor(message: string = "Content blocked by safety filters.") {
    super(message, "SAFETY_BLOCKED", false, 400);
    this.name = "SafetyBlockedError";
  }
}

/**
 * Invalid image data provided.
 */
export class InvalidImageError extends AppError {
  constructor(message: string = "Invalid or unsupported image.") {
    super(message, "INVALID_IMAGE", false, 400);
    this.name = "InvalidImageError";
  }
}

/**
 * Image exceeds the maximum allowed size.
 */
export class ImageTooLargeError extends AppError {
  constructor(maxSizeMB: number = 20) {
    super(
      `Image too large. Maximum allowed size is ${maxSizeMB} MB.`,
      "IMAGE_TOO_LARGE",
      false,
      413
    );
    this.name = "ImageTooLargeError";
  }
}

/**
 * Network or timeout errors that are safe to retry.
 */
export class RetryableNetworkError extends AppError {
  constructor(message: string = "Network error occurred. Retrying...") {
    super(message, "NETWORK_ERROR", true, 503);
    this.name = "RetryableNetworkError";
  }
}

/**
 * Timeout during API call.
 */
export class TimeoutError extends AppError {
  constructor(message: string = "Request timed out.") {
    super(message, "TIMEOUT", true, 504);
    this.name = "TimeoutError";
  }
}

/**
 * Failed to parse the AI response into structured JSON.
 */
export class ParseError extends AppError {
  constructor(message: string = "Failed to parse AI response.") {
    super(message, "PARSE_FAILURE", true, 500);
    this.name = "ParseError";
  }
}
