declare module 'framer-motion' {
  import * as React from 'react';

  export interface AnimatePresenceProps {
    children: React.ReactNode;
    mode?: 'sync' | 'wait' | 'popLayout';
    initial?: boolean;
    onExitComplete?: () => void;
    exitBeforeEnter?: boolean;
    presenceAffectsLayout?: boolean;
  }

  export const AnimatePresence: React.FC<AnimatePresenceProps>;

  export interface MotionProps {
    initial?: any;
    animate?: any;
    exit?: any;
    transition?: any;
    whileHover?: any;
    whileTap?: any;
    layout?: boolean | string;
    layoutId?: string;
    className?: string;
    style?: React.CSSProperties;
    [key: string]: any;
  }

  export const motion: {
    [key in keyof JSX.IntrinsicElements]: React.ForwardRefExoticComponent<
      MotionProps & JSX.IntrinsicElements[key]
    >;
  };
}

declare module '*.css' {
  const content: { [className: string]: string };
  export default content;
}

declare module '*.svg' {
  import * as React from 'react';
  export const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement>>;
  const src: string;
  export default src;
}

declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

declare module '*.json' {
  const content: any;
  export default content;
}

declare namespace NodeJS {
  interface ProcessEnv {
    REACT_APP_API_URL: string;
    REACT_APP_MESSAGES_STORAGE_KEY: string;
    NODE_ENV: 'development' | 'production' | 'test';
  }
} 