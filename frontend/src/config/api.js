const API_CONFIG = {
  LOGIN_SERVICE: {
    BASE_URL: '',
    LOGIN: '/login',
    REGISTER: '/register'
  },
  PAPER_MARKING_SERVICE: {
    BASE_URL: '',
    CORRECT: '/correct'
  },
  PAPER_COMPOSITION_SERVICE: {
    BASE_URL: '',
    GENERATE_QUIZ: '/generate_quiz'
  },
  ACHIEVEMENT_ANALYSIS_SERVICE: {
    BASE_URL: '',
    ANALYZE: '/analyze'
  },
  CODE_CORRECTION_SERVICE: {
    BASE_URL: '',
    REVIEW_CODE: '/review_code',
    ENDPOINTS: {
      CHAT: '/api/mentor/chat',
      EXPLAIN: '/api/mentor/explain',
      PROMPT_CHECK: '/api/mentor/prompt_check',
      RESET: '/api/mentor/reset',
      HEALTH: '/health'
    }
  },
  PROMPT_ARENA_SERVICE: {
    BASE_URL: '',
    ENDPOINTS: {
      NEW_QUEST: '/api/prompt_arena/new_quest',
      SIMULATE: '/api/prompt_arena/simulate',
      JUDGE: '/api/prompt_arena/judge',
      HEALTH: '/api/prompt_arena/health'
    }
  },
  DIGITAL_HUMAN_SERVICE: {
    BASE_URL: '',
    ENDPOINTS: {
      SYNTHESIZE: '/api/synthesize',
      SYNTHESIZE_VIDEO: '/api/synthesize_video',
      AUDIO: '/api/audio',
      VIDEO: '/api/video',
      VOICES: '/api/voices',
      HEALTH: '/api/health'
    }
  },
  AI_TEACHING_SERVICE: {
    BASE_URL: '',
    ENDPOINTS: {
      HEALTH: '/api/ai-teaching/health',
      THEORY_CONTENT: '/api/ai-teaching/theory/content',
      THEORY_COMPARISON: '/api/ai-teaching/theory/comparison',
      ENV_CHECK: '/api/ai-teaching/environment/check',
      RESNET_MODELS: '/api/ai-teaching/resnet/models',
      RESNET_STRUCTURE: '/api/ai-teaching/resnet/structure',
      LOAD_MODEL: '/api/ai-teaching/resnet/load-model',
      DATASET_INFO: '/api/ai-teaching/dataset/info',
      PREPROCESSING_STEPS: '/api/ai-teaching/preprocessing/steps',
      PREPROCESSING_DEMO: '/api/ai-teaching/preprocessing/demo',
      TRAIN_START: '/api/ai-teaching/train/start',
      TRAIN_STATUS: '/api/ai-teaching/train/status',
      TRAIN_STOP: '/api/ai-teaching/train/stop',
      PREDICT: '/api/ai-teaching/predict',
      PROGRESS: '/api/ai-teaching/progress'
    }
  },
  YOLO_TEACHING_SERVICE: {
    BASE_URL: '',
    ENDPOINTS: {
      HEALTH: '/api/yolo-teaching/health',
      DETECTION_VS_CLASSIFICATION: '/api/yolo-teaching/theory/detection-vs-classification',
      PRINCIPLE: '/api/yolo-teaching/theory/principle',
      APPLICATIONS: '/api/yolo-teaching/theory/applications',
      ENV_CHECK: '/api/yolo-teaching/environment/check',
      MODELS_LIST: '/api/yolo-teaching/models/list',
      MODELS_STRUCTURE: '/api/yolo-teaching/models/structure',
      MODELS_CLASSES: '/api/yolo-teaching/models/classes',
      LABELING_TOOLS: '/api/yolo-teaching/labeling/tools',
      LABELING_FORMATS: '/api/yolo-teaching/labeling/formats',
      TRAINING_PARAMS: '/api/yolo-teaching/training/params',
      TRAIN_START: '/api/yolo-teaching/train/start',
      TRAIN_STATUS: '/api/yolo-teaching/train/status',
      TRAIN_STOP: '/api/yolo-teaching/train/stop',
      DETECT_IMAGE: '/api/yolo-teaching/detect/image',
      DETECT_VIDEO: '/api/yolo-teaching/detect/video-frame',
      PROGRESS: '/api/yolo-teaching/progress'
    }
  },
  API_MANAGEMENT_SERVICE: {
    BASE_URL: '',
    ENDPOINTS: {
      HEALTH: '/api/health',
      PROVIDERS: '/api/providers',
      CONFIG: '/api/config',
      CONFIG_STATUS: '/api/config/status',
      SINGLE_PROVIDER_STATUS: '/api/config/status',
      GLOBAL_SETTINGS: '/api/config/global',
      SYNC_TO_ENV: '/api/config/sync-to-env',
      TEST_CONNECTION: '/api/test-connection',
      CHECK_MODEL: '/api/check-model',
      OPENMAIC_PROVIDERS: '/api/openmaic/providers',
      OPENMAIC_RESOLVE_KEY: '/api/openmaic/resolve-key',
      OPENMAIC_RESOLVE_BASE_URL: '/api/openmaic/resolve-base-url'
    }
  },
  PRACTICE_SERVICE: {
    BASE_URL: '',
    ENDPOINTS: {
      HEALTH: '/health',
      GENERATE: '/api/practice/generate',
      SUBMIT: '/api/practice/submit',
      HISTORY: '/api/practice/history',
      HISTORY_DETAIL: '/api/practice/history',
      WRONG_QUESTIONS: '/api/practice/wrong-questions',
      WRONG_QUESTIONS_RETRY: '/api/practice/wrong-questions',
      WRONG_QUESTIONS_EXPORT: '/api/practice/wrong-questions/export',
      STATS: '/api/practice/stats',
      RADAR: '/api/practice/radar',
      LEADERBOARD: '/api/practice/leaderboard',
      LEADERBOARD_REFRESH: '/api/practice/leaderboard/refresh'
    }
  }
}

export function getApiUrl(service, endpoint) {
  const serviceConfig = API_CONFIG[service]
  if (!serviceConfig) {
    console.error(`Unknown service: ${service}`)
    return ''
  }
  return `${serviceConfig.BASE_URL}${serviceConfig.ENDPOINTS ? serviceConfig.ENDPOINTS[endpoint] : endpoint}`
}

export function getServiceUrl(serviceName) {
  const service = API_CONFIG[serviceName]
  if (!service) {
    console.error(`Unknown service: ${serviceName}`)
    return ''
  }
  return service.BASE_URL
}

export default API_CONFIG
