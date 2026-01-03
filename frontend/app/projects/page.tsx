'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

// Redirect to home page
export default function ProjectsPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/');
  }, [router]);

  return null;
}
