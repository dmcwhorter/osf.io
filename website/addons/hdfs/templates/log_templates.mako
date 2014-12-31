<script type="text/html" id="hdfs_file_added">
added file
<a class="overflow log-file-link" data-bind="click: NodeActions.addonFileRedirect, text: params.path"></a> to
bucket
<span data-bind="text: params.bucket"></span> in
<span data-bind="text: nodeType"></span>
<a class="log-node-title-link overflow" data-bind="attr: {href: nodeUrl}, text: nodeTitle"></a>
</script>

<script type="text/html" id="hdfs_file_updated">
updated file
<a class="overflow log-file-link" data-bind="click: NodeActions.addonFileRedirect, text: params.path"></a> in
bucket
<span data-bind="text: params.bucket"></span> in
<span data-bind="text: nodeType"></span>
<a class="log-node-title-link overflow" data-bind="attr: {href: nodeUrl}, text: nodeTitle"></a>
</script>

<script type="text/html" id="hdfs_file_removed">
removed file <span class="overflow" data-bind="text: params.path"></span> from
bucket
<span data-bind="text: params.bucket"></span> in
<span data-bind="text: nodeType"></span>
<a class="log-node-title-link overflow" data-bind="attr: {href: nodeUrl}, text: nodeTitle"></a>
</script>

<script type="text/html" id="hdfs_node_authorized">
authorized the Hdfs addon for {{ nodeType }}
<a class="log-node-title-link overflow"
    data-bind="attr: {href: nodeUrl}">{{ nodeTitle }}</a>
</script>

<script type="text/html" id="hdfs_node_deauthorized">
deauthorized the Hdfs addon for {{ nodeType }}
<a class="log-node-title-link overflow"
    data-bind="attr: {href: nodeUrl}">{{ nodeTitle }}</a>
</script>
