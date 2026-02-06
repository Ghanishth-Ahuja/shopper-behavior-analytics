import { useState, useEffect } from 'react';
import { useQuery } from 'react-query';

// Custom hook for API calls with loading states and error handling
export const useApi = (queryKey, apiFunction, options = {}) => {
  const [retryCount, setRetryCount] = useState(0);

  const {
    data,
    error,
    isLoading,
    isError,
    refetch,
    ...rest
  } = useQuery(
    queryKey,
    apiFunction,
    {
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      ...options,
    }
  );

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    refetch();
  };

  return {
    data,
    error,
    isLoading,
    isError,
    refetch,
    retry: handleRetry,
    retryCount,
    ...rest,
  };
};

// Custom hook for polling data
export const usePollingApi = (queryKey, apiFunction, interval = 30000, options = {}) => {
  return useApi(
    queryKey,
    apiFunction,
    {
      refetchInterval: interval,
      refetchIntervalInBackground: true,
      ...options,
    }
  );
};

// Custom hook for infinite scrolling
export const useInfiniteApi = (queryKey, apiFunction, options = {}) => {
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const {
    data,
    error,
    isLoading,
    isError,
    refetch,
    ...rest
  } = useApi(
    [queryKey, page],
    () => apiFunction(page),
    {
      ...options,
      onSuccess: (data) => {
        if (data.length === 0 || data.length < (options.pageSize || 20)) {
          setHasMore(false);
        }
      },
    }
  );

  const loadMore = () => {
    if (!isLoading && hasMore) {
      setPage(prev => prev + 1);
    }
  };

  const reset = () => {
    setPage(1);
    setHasMore(true);
  };

  return {
    data,
    error,
    isLoading,
    isError,
    refetch,
    loadMore,
    reset,
    hasMore,
    page,
    ...rest,
  };
};

// Custom hook for debounced API calls
export const useDebouncedApi = (queryKey, apiFunction, delay = 500, options = {}) => {
  const [debouncedQueryKey, setDebouncedQueryKey] = useState(queryKey);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQueryKey(queryKey);
    }, delay);

    return () => clearTimeout(timer);
  }, [queryKey, delay]);

  return useApi(debouncedQueryKey, apiFunction, options);
};

// Custom hook for API with caching
export const useCachedApi = (queryKey, apiFunction, cacheTime = 30 * 60 * 1000, options = {}) => {
  return useApi(
    queryKey,
    apiFunction,
    {
      cacheTime,
      staleTime: cacheTime,
      ...options,
    }
  );
};

export default useApi;
