import { ClerkProvider } from '@clerk/nextjs';
import { viVN } from '@clerk/localizations';
import type { AppProps } from 'next/app';
import 'react-datepicker/dist/react-datepicker.css';
import '../styles/globals.css';

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ClerkProvider {...pageProps} localization={viVN}>
      <Component {...pageProps} />
    </ClerkProvider>
  );
}