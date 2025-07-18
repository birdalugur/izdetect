<!-- src/components/LabelTag.svelte -->
<script>
  export let labelKey = '';
  export let labelValue = '';
  export let size = 'sm'; // 'xs', 'sm', 'md', 'lg'
  
  $: sizeClasses = {
    'xs': 'px-2 py-0.5 text-xs',
    'sm': 'px-3 py-1 text-xs',
    'md': 'px-4 py-2 text-sm',
    'lg': 'px-5 py-2 text-base'
  };
  
  $: iconSizes = {
    'xs': 'w-2 h-2',
    'sm': 'w-3 h-3',
    'md': 'w-4 h-4',
    'lg': 'w-5 h-5'
  };
  
  $: colorScheme = {
    'insan': 'bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 border border-green-200',
    'arac': 'bg-gradient-to-r from-blue-100 to-sky-100 text-blue-800 border border-blue-200',
    'hayvan': 'bg-gradient-to-r from-orange-100 to-amber-100 text-orange-800 border border-orange-200'
  };
  
  $: defaultScheme = 'bg-gradient-to-r from-gray-100 to-slate-100 text-gray-800 border border-gray-200';
</script>

<span 
  class="rounded-full font-semibold flex items-center gap-1 shadow-sm transition-all duration-200 hover:scale-105 
         {sizeClasses[size]} 
         {colorScheme[labelKey] || defaultScheme}"
  title="{labelKey}: {labelValue}"
>
  <!-- İkonlar -->
  {#if labelKey === 'insan'}
    <svg xmlns="http://www.w3.org/2000/svg" class="{iconSizes[size]}" fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
    </svg>
  {:else if labelKey === 'arac'}
    <svg xmlns="http://www.w3.org/2000/svg" class="{iconSizes[size]}" fill="currentColor" viewBox="0 0 24 24">
      <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.22.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>
    </svg>
  {:else if labelKey === 'hayvan'}
    <svg xmlns="http://www.w3.org/2000/svg" class="{iconSizes[size]}" fill="currentColor" viewBox="0 0 24 24">
      <path d="M4.5 12c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5-.67 1.5-1.5 1.5-1.5-.67-1.5-1.5zm11-1.5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5-1.5-.67-1.5-1.5.67-1.5 1.5-1.5zm5.5 1.5c0 .83-.67 1.5-1.5 1.5s-1.5-.67-1.5-1.5.67-1.5 1.5-1.5 1.5.67 1.5 1.5zm-10 6.5c-2.76 0-5-2.24-5-5 0-.34.04-.67.09-1h2.84c-.59.58-1.43 1-2.43 1v2c2.21 0 4 1.79 4 4 0 .34-.04.67-.09 1h2.84c-.59-.58-1.43-1-2.43-1v-2z"/>
    </svg>
  {:else}
    <!-- Genel etiket ikonu -->
    <svg xmlns="http://www.w3.org/2000/svg" class="{iconSizes[size]}" fill="currentColor" viewBox="0 0 24 24">
      <path d="M17.63 5.84C17.27 5.33 16.67 5 16 5L5 5.01C3.9 5.01 3 5.9 3 7v10c0 1.1.9 2 2 2h11c.67 0 1.27-.33 1.63-.84L22 12l-4.37-6.16z"/>
    </svg>
  {/if}
  
  {labelValue}
</span> 