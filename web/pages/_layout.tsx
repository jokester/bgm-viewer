import { ComponentChildren } from 'preact';
import { PageProps } from './_shared';

interface LayoutProps extends PageProps {
  children: ComponentChildren;
}

interface NavItem {
  label: string;
  path: string;
  icon?: string;
}

const navigationItems: NavItem[] = [
  {label: '主页', path: '/', icon: '🏠'},
  {label: '作品', path: '/subjects', icon: '📚'},
  // { label: '章节', path: '/episodes', icon: '📺' },
  {label: '角色', path: '/characters', icon: '👤'},
  {label: '人物', path: '/people', icon: '👥'},
  {label: '网络', path: '/network', icon: '🕸️'},
];

const shortcuts = [
  {label: 'Recent', path: '/recent', icon: '⏰'},
  {label: 'Popular', path: '/popular', icon: '🔥'},
  {label: 'Random', path: '/random', icon: '🎲'},
];

export function Layout({children, path}: LayoutProps) {
  const isActivePath = (navPath: string) => {
    if (navPath === '/') {
      return path === '/';
    }
    return path?.startsWith(navPath);
  };

  return (
    <div className='min-h-screen bg-gray-50'>
      {/* Navigation Header */}
      <nav className='bg-white shadow-sm border-b border-gray-200'>
        <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='flex justify-between items-center h-16'>
            {/* Logo and Brand */}
            <div className='flex items-center'>
              <div className='flex-shrink-0'>
                <h1 className='text-xl font-bold text-gray-900'>
                  Bangumi Archive Viewer
                </h1>
              </div>
            </div>

            {/* Main Navigation */}
            <div className='hidden md:block'>
              <div className='ml-10 flex items-baseline space-x-4'>
                {navigationItems.map((item) => (
                  <a
                    key={item.path}
                    href={item.path}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActivePath(item.path)
                        ? 'bg-blue-100 text-blue-700 border border-blue-200'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <span className='mr-2'>{item.icon}</span>
                    {item.label}
                  </a>
                ))}
              </div>
            </div>

            {/* Shortcuts */}
            <div className='hidden lg:flex items-center space-x-2'>
              {shortcuts.map((shortcut) => (
                <a
                  key={shortcut.path}
                  href={shortcut.path}
                  className='px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors'
                  title={shortcut.label}
                >
                  <span className='text-lg'>{shortcut.icon}</span>
                </a>
              ))}
            </div>

            {/* Mobile menu button */}
            <div className='md:hidden'>
              <button
                type='button'
                className='bg-white p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500'
                aria-controls='mobile-menu'
                aria-expanded='false'
              >
                <span className='sr-only'>Open main menu</span>
                <svg
                  className='block h-6 w-6'
                  xmlns='http://www.w3.org/2000/svg'
                  fill='none'
                  viewBox='0 0 24 24'
                  stroke='currentColor'
                  aria-hidden='true'
                >
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    strokeWidth={2}
                    d='M4 6h16M4 12h16M4 18h16'
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className='md:hidden' id='mobile-menu'>
          <div className='px-2 pt-2 pb-3 space-y-1 sm:px-3'>
            {navigationItems.map((item) => (
              <a
                key={item.path}
                href={item.path}
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  isActivePath(item.path)
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <span className='mr-2'>{item.icon}</span>
                {item.label}
              </a>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className='max-w-7xl mx-auto py-6 sm:px-6 lg:px-8'>
        <div className='px-4 py-6 sm:px-0'>
          {children as any}
        </div>
      </main>

      {/* Footer */}
      <footer className='bg-white border-t border-gray-200 mt-auto'>
        <div className='max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8'>
          <div className='text-center text-sm text-gray-500'>
            <p>BGM Archive Viewer - Bangumi Data Analysis Platform</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
