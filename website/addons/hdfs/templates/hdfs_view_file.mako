<%inherit file="project/addon/view_file.mako" />
<%def name="title()">${file_name}</%def>

<%def name="file_versions()">
    <div id='hdfsScope' class="scripted">

        <div class="alert alert-warning" data-bind="visible: deleting">
            Deleting your file…
        </div>

            <p>
                % if download_url:
                    <!--download button-->
                    <a class="btn btn-success btn-md" href="${download_url}">
                        Download <i class="icon-download-alt"></i></a>
                % endif
                % if user['can_edit'] and 'write' in user['permissions']:
                    <!--delete button-->
                    <a href="#" data-bind="visible: api_url, click: deleteFile" class="btn btn-danger btn-md" >
                        Delete <i class="icon-trash"></i>
                    </a>
            </p>
        % endif

    </div>
    <script type="text/javascript">
        window.contextVars = $.extend(true, {}, window.contextVars, {
            node: {
                urls: {
                    delete_url: '${delete_url}',
                    files_page_url: '${files_page_url}'
                    }
            }
        });
    </script>
</%def>

<%def name="javascript_bottom()">
${parent.javascript_bottom()}
<script src="/static/public/js/hdfs/file-detail.js"></script>
</%def>
