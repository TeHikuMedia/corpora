const BundleTracker = require('webpack-bundle-tracker');

const pages = {
  vue_app_01: {
    entry: './src/main.ts',
    chunks: ['chunk-vendors'],
  },
};

const publicPath = process.env.ENV_TYPE !== 'local'
  ? 'https://'+process.env.AWS_CLOUDFRONT_CNAME+'/vue_bundles/' // need to put this in ansible
  : 'https://localhost:8003/'

module.exports = {
  pages,
  filenameHashing: true,
  productionSourceMap: false,
  publicPath: publicPath,
  outputDir: '../corpora/static/vue_bundles/',
  chainWebpack: (config) => {
    config.optimization
      .splitChunks({
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'chunk-vendors',
            chunks: 'all',
            priority: 1,
          },
        },
      });

    Object.keys(pages).forEach((page) => {
      config.plugins.delete(`html-${page}`);
      config.plugins.delete(`preload-${page}`);
      config.plugins.delete(`prefetch-${page}`);
    });

    config
      .plugin('BundleTracker')
      .use(BundleTracker, [{
        filename: '../corpora/static/vue_bundles/webpack-stats.json' }
      ]);

    config.devServer
      .host('0.0.0.0')
      .port(8003)
      .public('https://localhost:8003/')
      .hotOnly(true)
      .watchOptions({ poll: true })
      .https(true)
      .disableHostCheck(true)
      .headers({ 'Access-Control-Allow-Origin': ['*'] });
  },
};
