import React, { useState } from 'react';
import { Menu } from 'lucide-react';
import ChatBox from '../components/ChatBox';
import Sidebar from '../components/Sidebar';

const Home = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen w-full bg-surface-base overflow-hidden relative">
      <Sidebar isOpen={isSidebarOpen} setIsOpen={setIsSidebarOpen} />
      
      {/* Mobile Hamburger Button */}
      <button 
        onClick={() => setIsSidebarOpen(true)}
        className="md:hidden absolute top-4 left-4 z-30 p-2 text-text-secondary hover:text-text-primary bg-surface-base rounded-md"
      >
        <Menu size={24} />
      </button>

      <div className="flex-1 relative h-full">
        <ChatBox />
      </div>
    </div>
  );
};

export default Home;
