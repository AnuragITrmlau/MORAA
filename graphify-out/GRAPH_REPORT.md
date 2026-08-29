# Graph Report - Moraa Gemvision  (2026-08-26)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1899 nodes · 3484 edges · 118 communities (94 shown, 24 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 155 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `07227cae`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ProcessingService
- app/schemas/__init__.py
- gemini.service.ts
- routes/analysis.py
- User
- auth_service.py
- BaseAIProvider
- prompt_generation_service.py
- cn
- ai/__init__.py
- config.py
- ImageGenerationManager
- routes/tracking.py
- upload_service.py
- ProductFidelity
- prompt_fusion_engine.py
- analysis.ts
- OpenAIImageProvider
- compilerOptions
- index.ts
- get_marketplace_presentation
- routes/image_generation.py
- earring_ecommerce.py
- test_amazon_india_presentation.py
- logger.py
- page.tsx
- GeminiImageProvider
- TestAmazonPresentationContent
- TestErrorClassification
- evaluate_fidelity
- test_product_fidelity.py
- .analyze
- PreprocessingService
- PromptEditorPage.tsx
- ui-store.ts
- devDependencies
- logger.ts
- BaseRepository
- PromptGenerationPanel.tsx
- AIProviderManager
- generate_prompts
- BaseAiProvider
- dependencies
- ThemeContext.tsx
- routes/prompt_fusion.py
- Settings
- task3_experiment.py
- run_pilot.py
- image-analysis.service.ts
- PhotoFilterPanel.tsx
- prompt-generation.service.ts
- upload.py
- AiResponse
- TestAmazonNoRedesign
- _make_mock_provider
- .generate_image
- LocalVisionProvider
- .log_processing_step
- GeminiProvider
- AnalysisPipeline
- upload_images_batch
- rate_limit.py
- get_amazon_india_earrings_presentation
- logging_middleware.py
- OpenAIProvider
- HistoryPage.tsx
- ClaudeProvider
- OpenAIProvider
- ModelType
- analysis_group.py
- TestConstants
- TestBackwardCompatibility
- manifest.json
- frontend/package.json
- Logger
- FidelityMetal
- measure_colours
- env.py
- .analyze_image
- generate-image/route.ts
- AssistantPanel.tsx
- CompetitorTable.tsx
- routes/__init__.py
- JSONType
- generate/route.ts
- cors.py
- .get
- TestProviderRoutingUnchanged
- @google/genai
- GroupAnalysisTask
- TestPFIERemainsDisabled
- prompt_health
- task5_prompt_experiment.py
- api_analyze_test.py
- api_gen_test.py
- middleware/__init__.py
- app/services/__init__.py
- utils/__init__.py
- ._build_default_prompt
- .classify_error
- .is_permanent
- ._measure
- .model_name
- .provider_name
- backend/schemas/__init__.py
- backend/services/__init__.py
- .test_empty_model
- eslint.config.mjs
- next.config.ts
- next
- react-hook-form
- tailwind-merge
- postcss.config.mjs
- make_test_image.py
- product_fidelity.py

## God Nodes (most connected - your core abstractions)
1. `ImageGenerationManager` - 51 edges
2. `ProcessingService` - 49 edges
3. `ProductFidelity` - 33 edges
4. `cn()` - 31 edges
5. `BaseRepository` - 29 edges
6. `Image` - 27 edges
7. `Base` - 25 edges
8. `OpenAIImageProvider` - 25 edges
9. `User` - 25 edges
10. `get_marketplace_presentation()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `run_gemini_test()` --uses--> `ImageGenerationManager`  [INFERRED]
  data/golden/earrings/run_pilot.py → backend/app/ai/image_generation_manager.py
- `run_gemini_test()` --calls--> `get_amazon_india_earrings_presentation()`  [INFERRED]
  data/golden/earrings/run_pilot.py → backend/app/ai/marketplaces/amazon_india.py
- `generate_prompts()` --uses--> `Analysis`  [INFERRED]
  backend/app/api/routes/prompts.py → backend/app/models/analysis.py
- `AnalysisService` --uses--> `Analysis`  [INFERRED]
  backend/app/services/analysis_service.py → backend/app/models/analysis.py
- `ReportService` --uses--> `Analysis`  [INFERRED]
  backend/app/services/report_service.py → backend/app/models/analysis.py

## Import Cycles
- None detected.

## Communities (118 total, 24 thin omitted)

### Community 0 - "ProcessingService"
Cohesion: 0.05
Nodes (61): Base, Database engine, session factory, and declarative base., Declarative base for all database models., set_sqlite_pragma(), Analysis, Analysis model for jewellery image analysis results., Jewellery analysis result model. Every analysis is permanently linked to its…, AuditLog (+53 more)

### Community 1 - "app/schemas/__init__.py"
Cohesion: 0.06
Nodes (53): delete_history_item(), get_history(), get_history_item(), get_history_stats(), get, Session, Delete a history entry., Get paginated analysis history. (+45 more)

### Community 2 - "gemini.service.ts"
Cohesion: 0.05
Nodes (41): AppError, GeminiError, GroqError, ImageTooLargeError, InvalidImageError, ParseError, QuotaExceededError, RetryableNetworkError (+33 more)

### Community 3 - "routes/analysis.py"
Cohesion: 0.06
Nodes (45): AnalysisResponse, analyze_image(), analyze_image_sync(), get_analysis(), get_analysis_timeline(), list_analyses(), get, post (+37 more)

### Community 4 - "User"
Cohesion: 0.06
Nodes (42): get_current_user(), Session, FastAPI dependencies for authentication and database sessions., Get the current authenticated user from JWT token. Returns None if no token…, Require authentication - raises 401 if no valid token., require_auth(), Prompt generation API routes. Uses the EXISTING analysis result from the…, download_report() (+34 more)

### Community 5 - "auth_service.py"
Cohesion: 0.08
Nodes (43): login(), post, Session, Authentication API routes., Register a new user account., Authenticate user and return JWT tokens., Refresh an expired access token., refresh_token() (+35 more)

### Community 6 - "BaseAIProvider"
Cohesion: 0.07
Nodes (24): AI Provider Manager — orchestrates analysis across multiple AI providers. The…, BaseAIProvider, ProviderResult, ABC, Any, Abstract base class for all AI providers in the Provider Manager. Every…, Standardised result returned by every provider., Abstract base for an AI analysis provider. Each provider wraps a specific AI… (+16 more)

### Community 7 - "prompt_generation_service.py"
Cohesion: 0.08
Nodes (35): on_worker_ready(), on_worker_shutdown(), Celery application instance for MORAA GemVision. Usage (development — eager…, Log when the Celery worker starts., Log when the Celery worker shuts down., _build_workflow_analysis(), _esc(), _generate_complementary_shot() (+27 more)

### Community 8 - "cn"
Cohesion: 0.07
Nodes (26): ChartCard(), ChartCardProps, defaultData, maxPrice, minPrice, PricePoint, ImageComparison(), ImagePanel() (+18 more)

### Community 9 - "ai/__init__.py"
Cohesion: 0.09
Nodes (21): AIEngine, ABC, Abstract base class for AI analysis engines. This defines the interface that…, Abstract base for AI analysis engines., Validate that the image is suitable for analysis. Args: image_path: Path to the…, Return the name/identifier of this AI engine., Return the version of this AI engine., create_engine() (+13 more)

### Community 10 - "config.py"
Cohesion: 0.08
Nodes (22): Image Generation Manager — orchestrates image generation across multiple AI…, Gemini Image Generation provider — uses Gemini image-capable models via the…, BaseImageGenerationProvider, ImageGenerationResult, ABC, Any, Abstract base class for AI image generation providers. Every image generation…, Standardised result returned by every image generation provider. (+14 more)

### Community 11 - "ImageGenerationManager"
Cohesion: 0.09
Nodes (23): ImageGenerationManager, Orchestrates image generation with automatic provider failover. The manager: -…, main(), Task 4 controlled test: invoke the unchanged provider paths with one reference., run(), patch, Verify the reference priority block is appended correctly., REFERENCE_PRIORITY_BLOCK is appended when reference_image is provided. (+15 more)

### Community 12 - "routes/tracking.py"
Cohesion: 0.11
Nodes (34): get_processing_logs(), get_request_by_image(), get_retry_history(), get_timeline(), get_tool_execution_logs(), get_version_history(), get, Session (+26 more)

### Community 13 - "upload_service.py"
Cohesion: 0.10
Nodes (29): Upload service for handling image file uploads. Every uploaded image receives a…, Delete an image, its file, and its isolated request directory., Image upload management service., Validate uploaded file., Process and save an uploaded image. Generates a globally unique ``request_id``,…, UploadService, delete_directory(), delete_file() (+21 more)

### Community 14 - "ProductFidelity"
Cohesion: 0.11
Nodes (20): build_fidelity_instruction(), _fmt_list(), ProductFidelity, Master product identity — the single source of truth. Every field is optional.…, Format a list of strings as a comma-separated string., Build the canonical product fidelity instruction for image-generation prompts.…, When fidelity has no fields populated, returns fidelity header + reference…, Instruction includes the product type when known. (+12 more)

### Community 15 - "prompt_fusion_engine.py"
Cohesion: 0.10
Nodes (28): fuse_prompt_health(), get, Health check for the prompt fusion engine., _build_facts_block(), _build_scale_control_block(), _creative_direction_via_chatgpt(), _creative_direction_via_template(), _first_value() (+20 more)

### Community 16 - "analysis.ts"
Cohesion: 0.10
Nodes (24): AnalysisResultPanel(), AnalysisResultPanelProps, ConfidenceBadge(), containerVariants, GeneralDisplay(), itemVariants, JewelleryDisplay(), ALLOWED_MIME_TYPES (+16 more)

### Community 17 - "OpenAIImageProvider"
Cohesion: 0.09
Nodes (16): OpenAIImageProvider, Any, AI image generation provider using OpenAI DALL-E / gpt-image-1., Check if the configured model supports image editing., Generate an image using OpenAI. When the model supports image editing (gpt-…, patch, When reference image is absent, identity anchor is NOT added., Prompt containing scene + REFERENCE_PRIORITY_BLOCK + Amazon marketplace is… (+8 more)

### Community 18 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 19 - "index.ts"
Cohesion: 0.09
Nodes (17): MOCK_COMPETITORS, MOCK_MARKET_DATA, MOCK_PRICE_POINTS, MOCK_RISKS, MOCK_SEO, MOCK_TRENDS, GeneratedReport, CompetitorProduct (+9 more)

### Community 20 - "get_marketplace_presentation"
Cohesion: 0.13
Nodes (14): get_marketplace_presentation(), Look up a marketplace presentation by its identifier. Args: marketplace_id: The…, generate_one(), main(), Path, Prompt Experiment — find the smallest reliable prompt for earring e-commerce.…, Generate one image for one variant + one reference., Verify marketplace registry resolution. (+6 more)

### Community 21 - "routes/image_generation.py"
Cohesion: 0.10
Nodes (21): generate_image(), image_generation_health(), get, post, API routes for AI image generation. Generates images using the…, Health check for the image generation service., Generate an image from a text prompt with automatic provider failover. Flow: 1.…, ImageGenerationHealthResponse (+13 more)

### Community 22 - "earring_ecommerce.py"
Cohesion: 0.11
Nodes (21): earring_ecommerce_health(), EarringEcommercePromptRequest, EarringEcommercePromptResponse, generate_earring_ecommerce_prompt(), BaseModel, get, post, API routes for Earring E-Commerce Main Image Prompt Generation. Provides a… (+13 more)

### Community 23 - "test_amazon_india_presentation.py"
Cohesion: 0.17
Nodes (11): Amazon India — Fashion Jewellery Earrings Main/Product Image Presentation.…, MarketPlacePresentation, Marketplace Presentation Layer — GemVision. Marketplace-specific presentation…, Lightweight container for a marketplace's presentation rules. Attributes:…, Marketplace Presentation Registry — GemVision. Maps marketplace string…, Tests for the Amazon India Marketplace Presentation Layer. Verifies: 1.…, Verify the MarketPlacePresentation dataclass contract., Dataclass has required fields. (+3 more)

### Community 24 - "logger.py"
Cohesion: 0.12
Nodes (19): Batch upload API route — upload multiple images for one analysis. All uploaded…, init_db(), Create all database tables. Imports every model to register it with…, lifespan(), FastAPI, get, MORAA GemVision - Main FastAPI Application Entry Point., Root endpoint with API information. (+11 more)

### Community 25 - "page.tsx"
Cohesion: 0.19
Nodes (15): Home(), pages, pageVariants, FooterBar(), DashboardPage(), NewAnalysisPage(), ReportItem, ReportsPage() (+7 more)

### Community 26 - "GeminiImageProvider"
Cohesion: 0.11
Nodes (15): GeminiImageProvider, Any, AI image generation provider using Google Gemini image-capable models., Gemini supports multimodal input (text + images)., Generate an image using Gemini's image-capable models. Uses…, generate_one(), main(), Path (+7 more)

### Community 27 - "TestAmazonPresentationContent"
Cohesion: 0.09
Nodes (12): Block restricts text, logos, watermarks, badges, borders., Block restricts props, packaging, lifestyle elements., Block requires product to be clearly visible and in focus., Default aspect ratio is 1:1., Marketplace ID matches expected value., Metadata dict is populated with marketplace info., Verify the Amazon India presentation block contains correct rules., Amazon presentation block is a non-empty string. (+4 more)

### Community 28 - "TestErrorClassification"
Cohesion: 0.16
Nodes (8): _is_non_recoverable_error(), _is_recoverable_error(), Check if an error is definitively non-recoverable., Check if an error is recoverable and should trigger a fallback., Tests for the image generation pipeline. Verifies: 1. Provider chain order —…, Verify the recoverable / non-recoverable error classification., A generic error that doesn't match any pattern., TestErrorClassification

### Community 29 - "evaluate_fidelity"
Cohesion: 0.13
Nodes (13): evaluate_fidelity(), Any, Evaluate how well a generated image matches the product fidelity spec. This is…, Verify the fidelity QA evaluation., When fidelity is None, returns manual QA note., When generated_attributes is None, returns manual QA note., Correct stone count is detected., Incorrect stone count is detected. (+5 more)

### Community 30 - "test_product_fidelity.py"
Cohesion: 0.17
Nodes (18): FidelityAttachment, FidelityDecorative, FidelityProportions, FidelityQAResult, FidelityStone, _fmt_stones(), BaseModel, How the jewellery attaches (hook, post, clasp, etc.). (+10 more)

### Community 31 - ".analyze"
Cohesion: 0.10
Nodes (20): _build_summary(), _closest_colour_name(), _detect_gemstone_hotspots(), _dominant_colours(), _estimate_image_quality(), _estimate_metal_type(), _estimate_price(), _estimate_weight() (+12 more)

### Community 32 - "PreprocessingService"
Cohesion: 0.11
Nodes (14): Any, Analyse multiple images using the AI Provider Manager. This is the core…, ImagePreprocessingError, PreprocessingResult, PreprocessingService, Image preprocessing service — prepares images before AI analysis. Performs: -…, Preprocess a single image: validate, resize, compress. Args: file_path:…, Preprocess multiple images in parallel. Args: file_paths: List of absolute… (+6 more)

### Community 33 - "PromptEditorPage.tsx"
Cohesion: 0.16
Nodes (17): buildInitialDrafts(), CATEGORY_COLORS, CATEGORY_ICONS, Drafts, FIELD_HINTS, PromptEditorPage(), DEFAULT_PROMPT_TEMPLATES, PROMPT_TEMPLATE_FIELDS (+9 more)

### Community 34 - "ui-store.ts"
Cohesion: 0.15
Nodes (13): AnalysisResponse, analyzeProduct(), getLastUploadResponse(), initialMultiUpload, initialUpload, UIState, AnalysisResult, ComparisonInfo (+5 more)

### Community 35 - "devDependencies"
Cohesion: 0.11
Nodes (19): eslint, eslint-config-next, devDependencies, eslint, eslint-config-next, tailwindcss, tailwindcss-animate, @tailwindcss/postcss (+11 more)

### Community 36 - "logger.ts"
Cohesion: 0.15
Nodes (16): PromptGenerationPanel(), generateRequestId(), LOG_LEVEL_PRIORITY, LogEntry, LogLevel, LogMeta, BackendUploadResponse, generatePromptsViaBackend() (+8 more)

### Community 37 - "BaseRepository"
Cohesion: 0.11
Nodes (10): BaseRepository, Base repository with standard database operations., Count records with optional filters., Repository pattern implementations package., Session, Session, Session, Session (+2 more)

### Community 38 - "PromptGenerationPanel.tsx"
Cohesion: 0.15
Nodes (12): CATEGORY_COLORS, CATEGORY_ICONS, containerVariants, itemVariants, PromptGenerationPanelProps, NOTE: setState updaters must stay pure — React may invoke them during the, AnalysisResult, GenerateImageRequest (+4 more)

### Community 39 - "AIProviderManager"
Cohesion: 0.15
Nodes (10): AIProviderManager, Any, Analyse images with automatic failover across providers. Args: image_paths:…, Return a list of available providers with status., Return the current provider chain order., Orchestrates AI analysis with automatic provider failover. The manager: -…, Lazy-initialise provider instances., Get a provider instance by name. (+2 more)

### Community 40 - "generate_prompts"
Cohesion: 0.16
Nodes (16): generate_prompts(), post, Session, Generate 8 promotional prompts using an existing analysis result. Looks up the…, Config, PromptGenerateRequest, PromptGenerateResponse, PromptProcessingResponse (+8 more)

### Community 41 - "BaseAiProvider"
Cohesion: 0.21
Nodes (10): BaseAiProvider, ABC, Abstract base class for all AI providers in the production architecture. Every…, Convenience: True if the error is transient or unrecognised., Abstract base for a production AI provider. Subclasses must implement…, Gemini AI provider — calls the Google Gemini API for image analysis. This is…, Production-ready AI Provider layer for MORAA GemVision. Every provider in this…, OpenAI provider — calls the OpenAI Vision API for image analysis. This is the… (+2 more)

### Community 42 - "dependencies"
Cohesion: 0.12
Nodes (17): class-variance-authority, clsx, framer-motion, dependencies, class-variance-authority, clsx, framer-motion, gsap (+9 more)

### Community 43 - "ThemeContext.tsx"
Cohesion: 0.16
Nodes (12): geistMono, geistSans, metadata, Header(), SettingsPage(), settingsSections, getInitialTheme(), Theme (+4 more)

### Community 44 - "routes/prompt_fusion.py"
Cohesion: 0.18
Nodes (14): fuse_prompt(), post, API routes for the Prompt Fusion Intelligence Engine (PFIE). GemVision V3 —…, Run the prompt fusion engine for a single category + mode., ProductIntelligence, PromptFusionLayer, PromptFusionRequest, PromptFusionResponse (+6 more)

### Community 45 - "Settings"
Cohesion: 0.13
Nodes (10): Path, Application settings loaded from environment variables/.env file., Return allowed extensions as a list., Return max upload size in bytes., Return CORS origins as a list., Check if using SQLite database., Return upload directory as Path., Return report directory as Path. (+2 more)

### Community 46 - "task3_experiment.py"
Cohesion: 0.17
Nodes (15): _base_prompt(), main(), Path, Task 3 — Controlled Prompt Experiment. Tests 4 prompt variants against 3…, Variant A: Current Task 1 prompt exactly as-is (baseline)., Variant B: Current prompt + explicit colour lock., Variant C: Current prompt + colour lock + remove "colour temperature" from MAY…, Variant D: Current prompt + colour/material lock + stronger reconstruction… (+7 more)

### Community 47 - "run_pilot.py"
Cohesion: 0.17
Nodes (15): call_api_generate(), _load_backend_env(), load_reference_base64(), main(), Phase 4D — Limited Real-Earring Controlled Generation Pilot This is a TEST-ONLY…, Execute an OpenAI test case via the API., Execute a Gemini test case by directly calling the provider., Load environment variables from backend/.env file. (+7 more)

### Community 48 - "image-analysis.service.ts"
Cohesion: 0.18
Nodes (13): dynamic, maxDuration, POST(), validateBody(), parseJsonResponse(), ALLOWED_MIME_TYPES, analyzeImage(), parseAnalysisResult() (+5 more)

### Community 49 - "PhotoFilterPanel.tsx"
Cohesion: 0.23
Nodes (12): FilterThumbnail(), PhotoFilterPanel(), PhotoFilterPanelProps, applyFilter(), applyFilterAsBlob(), clamp(), FilterDef, FilterId (+4 more)

### Community 50 - "prompt-generation.service.ts"
Cohesion: 0.30
Nodes (15): esc(), generateComplementaryShot(), generateFestive(), generateIngredientStory(), generateProfessionalShot(), generatePromptsFromWorkflowData(), generateScaleReference(), generateTransformation() (+7 more)

### Community 51 - "upload.py"
Cohesion: 0.15
Nodes (13): post, Session, UploadFile, Image upload API routes., Upload a jewellery image file. The file is validated for type and size, then…, upload_image(), Config, ImageResponse (+5 more)

### Community 52 - "AiResponse"
Cohesion: 0.23
Nodes (10): AiResponse, Standardised response returned by every AI provider. Fields ------ success :…, AiManager, Any, Call a single provider safely, catching any unexpected errors., Log a successful primary-provider response., Log a permanent failure — no fallback attempted., Log a successful fallback-provider response. (+2 more)

### Community 53 - "TestAmazonNoRedesign"
Cohesion: 0.13
Nodes (8): Verify the Amazon block contains NO product redesign instructions., Block does not redefine stone count., Block does not redefine metal colour., Block does not redefine product geometry., Block does not redefine decorative elements., Block does not redefine attachment mechanism., Block explicitly reinforces that the product must remain unchanged., TestAmazonNoRedesign

### Community 54 - "_make_mock_provider"
Cohesion: 0.18
Nodes (9): _make_mock_provider(), patch, marketplace=None preserves the existing aspect ratio., Unknown marketplace preserves the existing aspect ratio and does not crash., Amazon marketplace with no context aspect_ratio sets the default., The caller's original context dict must not be mutated., Create a mock provider that captures context., Amazon marketplace overrides frontend aspect ratio 4:5 to 1:1. (+1 more)

### Community 55 - ".generate_image"
Cohesion: 0.15
Nodes (9): _classify_error(), Any, Lazy-initialise provider instances., Get a provider instance by name., Build the ordered provider chain for image generation. Default: OpenAI gpt-…, Generate an image with automatic failover across providers. Args: prompt: The…, Return a list of available image generation providers with status., Return the current provider chain order. (+1 more)

### Community 56 - "LocalVisionProvider"
Cohesion: 0.16
Nodes (6): LocalVisionProvider, Any, Merge analysis results from multiple images into one unified result., Wraps the existing PIL-based VisionAIEngine as a provider. Uses the same engine…, Delegate to the engine's validate_image method., Analyse images using the local PIL-based vision engine. For multi-image…

### Community 57 - ".log_processing_step"
Cohesion: 0.15
Nodes (7): Any, Get all processing logs for a request, ordered by time., Mark a processing step as completed and calculate its duration. Expects a…, Mark a processing step as failed with error details., Get all tool execution logs for a request, ordered by execution order., Build a complete, ordered event timeline for a request. Merges processing logs,…, Record a processing step lifecycle event. Args: request_id: The upload request…

### Community 58 - "GeminiProvider"
Cohesion: 0.17
Nodes (6): GeminiProvider, Any, Add Gemini-specific status-code heuristics., Production Gemini provider for image analysis., Analyse a single image using Google Gemini. Args: image_data: Raw bytes of the…, Lazy-initialise provider instances.

### Community 59 - "AnalysisPipeline"
Cohesion: 0.20
Nodes (8): AnalysisPipeline, Any, Analyze a jewellery image and return structured results. The engine MUST read…, Orchestrates the analysis pipeline: preprocess -> AI engine -> postprocess.…, Run the full analysis pipeline. The pipeline always operates on the explicit…, Post-process the AI result to ensure consistent output format., get_analysis_pipeline(), Get or create the analysis pipeline (singleton per worker). Engine type is…

### Community 60 - "upload_images_batch"
Cohesion: 0.18
Nodes (12): post, Session, UploadFile, Upload multiple images and assign them to a single analysis group. Each image…, upload_images_batch(), BatchUploadImage, BatchUploadResponse, GroupAnalysisRequest (+4 more)

### Community 61 - "rate_limit.py"
Cohesion: 0.18
Nodes (9): BaseHTTPMiddleware, FastAPI, Request, RateLimitMiddleware, Simple in-memory rate limiting middleware., Simple in-memory rate limiter based on client IP., Check rate limit before processing request., Add rate limiting middleware. (+1 more)

### Community 62 - "get_amazon_india_earrings_presentation"
Cohesion: 0.20
Nodes (7): get_amazon_india_earrings_presentation(), Return the Amazon India fashion jewellery earrings main image presentation., Verify fidelity instructions come before marketplace instructions., When both are composed, fidelity text appears before marketplace text., REFERENCE_PRIORITY_BLOCK is still available and correct., Composed prompt preserves all fidelity text., TestCompositionOrder

### Community 63 - "logging_middleware.py"
Cohesion: 0.20
Nodes (9): BaseHTTPMiddleware, FastAPI, Request, Request logging middleware for API calls., Log all incoming requests and their response times., Process request, log it, and return response., Add request logging middleware., RequestLoggingMiddleware (+1 more)

### Community 64 - "OpenAIProvider"
Cohesion: 0.20
Nodes (5): OpenAIProvider, Any, Classify OpenAI API errors using their specific codes., Production OpenAI Vision provider for image analysis (fallback)., Analyse a single image using OpenAI Vision API. Args: image_data: Raw bytes of…

### Community 65 - "HistoryPage.tsx"
Cohesion: 0.33
Nodes (8): HistoryPage(), statusConfig, ProfilePage(), formatDate(), deleteHistoryItem(), getHistory(), getHistoryStats(), HistoryItem

### Community 66 - "ClaudeProvider"
Cohesion: 0.20
Nodes (5): ClaudeProvider, Any, AI provider using Anthropic Claude Vision API (stub)., Stub — always returns True., Stub — returns a placeholder result. TODO: Implement actual Anthropic Claude…

### Community 67 - "OpenAIProvider"
Cohesion: 0.20
Nodes (5): OpenAIProvider, Any, AI provider that uses OpenAI Vision API for image analysis., Validate image by checking it can be opened and base64-encoded., Analyse one or more images using OpenAI Vision API. For multi-image analysis,…

### Community 68 - "ModelType"
Cohesion: 0.15
Nodes (7): Any, Session, Get all records with pagination., Find records by field values., Find first record matching filter., Create multiple records at once., ModelType

### Community 69 - "analysis_group.py"
Cohesion: 0.20
Nodes (7): GroupAnalysisResponse, GroupAnalysisStatus, Schemas for multi-image analysis groups. Multiple images can be uploaded…, Response after starting a group analysis., Status of a group analysis., Get the current status of a group analysis. Queries the processing logs to…, Start analysis for a group of images. All images are analysed together through…

### Community 71 - "TestBackwardCompatibility"
Cohesion: 0.20
Nodes (6): Verify that constants imported from product_fidelity are usable by existing…, All constants can be imported directly from product_fidelity., REFERENCE_PRIORITY_BLOCK can still be imported from image_generation_manager., PRODUCT_PRESERVATION_BLOCK can still be imported from prompt_fusion_engine., REFERENCE_IMAGE_ANCHOR can still be imported from gemini_image_provider., TestBackwardCompatibility

### Community 72 - "manifest.json"
Cohesion: 0.22
Nodes (8): R1_A, R1_B, R1_C, R1_D, R2_A, R2_B, R2_C, R2_D

### Community 73 - "frontend/package.json"
Cohesion: 0.22
Nodes (8): name, private, scripts, build, dev, lint, start, version

### Community 75 - "FidelityMetal"
Cohesion: 0.29
Nodes (6): FidelityMetal, Metal appearance and finish., Verify the fidelity instruction respects the priority hierarchy., Fidelity rules appear before any presentation/lighting instructions., A model with only some fields populated is valid., TestPriorityOrder

### Community 76 - "measure_colours"
Cohesion: 0.32
Nodes (7): classify_pixel_hsv(), main(), measure_colours(), Path, Analyse V0-V7 experiment outputs for colour fidelity metrics. Measures gold%,…, Classify a pixel into gold/silver/skin/white/other based on HSV., Measure colour distribution in an image.

### Community 77 - "env.py"
Cohesion: 0.29
Nodes (5): Alembic environment configuration for database migrations., Run migrations in 'offline' mode., Run migrations in 'online' mode., run_migrations_offline(), run_migrations_online()

### Community 78 - ".analyze_image"
Cohesion: 0.29
Nodes (4): Any, Analyse a single image and return structured results. Args: image_data: Raw…, Safely parse JSON from a model response, stripping fences., Guarantee all required fields exist with safe defaults.

### Community 79 - "generate-image/route.ts"
Cohesion: 0.33
Nodes (5): dynamic, GenerateImageBody, maxDuration, POST(), validateBody()

### Community 80 - "AssistantPanel.tsx"
Cohesion: 0.52
Nodes (5): AssistantPanel(), getWelcomeMessage(), MOCK_RESPONSES, sendMessage(), AssistantMessage

### Community 81 - "CompetitorTable.tsx"
Cohesion: 0.38
Nodes (6): Competitor, CompetitorTable(), CompetitorTableProps, defaultCompetitors, getMatchLevel(), getStatus()

### Community 82 - "routes/__init__.py"
Cohesion: 0.33
Nodes (4): health_check(), get, Health check API route., Return service health status.

### Community 83 - "JSONType"
Cohesion: 0.33
Nodes (3): JSONType, Generic JSON type that works with both SQLite and PostgreSQL., TypeDecorator

### Community 84 - "generate/route.ts"
Cohesion: 0.47
Nodes (5): dynamic, maxDuration, POST(), validateBody(), generatePromptsFromAnalysis()

### Community 85 - "cors.py"
Cohesion: 0.50
Nodes (4): FastAPI, CORS middleware configuration., Configure CORS middleware for the FastAPI application., setup_cors()

### Community 87 - "TestProviderRoutingUnchanged"
Cohesion: 0.40
Nodes (4): patch, Verify provider routing is not affected by marketplace layer., Default provider chain is still [openai, gemini]., TestProviderRoutingUnchanged

### Community 88 - "@google/genai"
Cohesion: 0.40
Nodes (4): @google/genai, dependencies, @google/genai, @google/genai

### Community 89 - "GroupAnalysisTask"
Cohesion: 0.50
Nodes (3): GroupAnalysisTask, Task, Base task class for group analysis with error handling.

### Community 90 - "TestPFIERemainsDisabled"
Cohesion: 0.50
Nodes (3): Verify PFIE is still disabled., PFIE_ENABLED must be False., TestPFIERemainsDisabled

### Community 91 - "prompt_health"
Cohesion: 0.67
Nodes (3): prompt_health(), get, Health check for the prompt generation service.

### Community 92 - "task5_prompt_experiment.py"
Cohesion: 0.40
Nodes (5): generate_one(), main(), Path, Task 5 — Systematic Prompt Experiment for Earring E-Commerce. Phase 1-4: Create…, Generate one image for one variant + one reference.

### Community 117 - "product_fidelity.py"
Cohesion: 0.40
Nodes (3): Master Product Fidelity Layer — GemVision. Single source of truth for product…, main(), Prompt Experiment — Gemini fallback for failed variants. Completes V3-V7 using…

## Knowledge Gaps
- **170 isolated node(s):** `AnalysisDisplayData`, `GemstoneType`, `JewelleryType`, `MetalType`, `GeneratedReport` (+165 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ImageGenerationManager` connect `ImageGenerationManager` to `ai/__init__.py`, `config.py`, `run_pilot.py`, `test_amazon_india_presentation.py`, `routes/image_generation.py`, `earring_ecommerce.py`, `.generate_image`, `TestProviderRoutingUnchanged`, `_make_mock_provider`, `TestErrorClassification`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `ProcessingService` connect `ProcessingService` to `PreprocessingService`, `routes/analysis.py`, `analysis_group.py`, `BaseRepository`, `routes/tracking.py`, `upload_service.py`, `logger.py`, `.log_processing_step`, `upload_images_batch`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `AIProviderManager` connect `AIProviderManager` to `ProcessingService`, `ai/__init__.py`, `routes/analysis.py`, `BaseAIProvider`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `ImageGenerationManager` (e.g. with `BaseImageGenerationProvider` and `ImageGenerationResult`) actually correct?**
  _`ImageGenerationManager` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `ProcessingService` (e.g. with `upload_images_batch()` and `get_processing_logs()`) actually correct?**
  _`ProcessingService` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `ProductFidelity` (e.g. with `TestBuildFidelityInstruction` and `TestFidelityQA`) actually correct?**
  _`ProductFidelity` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AnalysisDisplayData`, `GemstoneType`, `JewelleryType` to the rest of the system?**
  _170 weakly-connected nodes found - possible documentation gaps or missing edges._