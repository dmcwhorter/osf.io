<div id="addContributors" class="modal fade">
    <div class="modal-dialog">
        <div id="addContributorsScope" class="modal-content">
            <div class="modal-header">
                <h3 data-bind="text:pageTitle"></h3>
            </div>

            <div class="modal-body">

                <!-- Whom to add -->

                <div data-bind="if: page() == 'whom'">

                    <!-- Find contributors -->
                    <form class='form'>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <input class='form-control' style="margin-bottom: 8px;"
                                            data-bind="value:query"
                                            placeholder='Search by name' autofocus/>
                                </div>
                                <div><button type='submit' class="btn btn-default" data-bind="click:search">Search</button></div>
                            </div>
                            <div class="col-md-6" data-bind="if:parentId">
                                <a data-bind="click:importFromParent, text:'Import contributors from ' + parentTitle"></a>
                            </div>
                            <div class="col-md-6">
                                <a data-bind="click:recentlyAdded, text:'Get list of recently added contributors'"></a>
                            </div>
                        </div>
                    </form>

                    <hr />

                    <!-- Choose which to add -->
                    <div class="row">

                        <div class="col-md-6">
                            <div>
                                <span class="modal-subheader">Results</span>
                                <a data-bind="click:addAll">Add all</a>
                            </div>
                            <div class="error">{{ errorMsg }}</div>
                            <table>
                                <tbody data-bind="foreach:{data:results, as: 'contributor', afterRender:addTips}">
                                    <tr data-bind="if:!($root.selected($data))">
                                        <td style="padding-right: 10px;">
                                            <a
                                                    class="btn btn-default contrib-button"
                                                    data-bind="click:$root.add"
                                                    rel="tooltip"
                                                    title="Add contributor"
                                                >+</a>
                                        </td>
                                        <td>
                                            <img data-bind="attr: {src: contributor.gravatar}" />
                                        </td>
                                        <td><span class="contributor-name">{{contributor.fullname}}</span></td>
                                    </tr>
                                </tbody>
                            </table>
                            <!-- Link to add non-registered contributor -->
                            <div class='help-block'>
                                <div data-bind='if: foundResults'>
                                    If the person you are looking for is not listed above, try a more specific search or <strong><a href="#"
                                    data-bind="click:gotoInvite">add <em>{{query}}</em> as an unregistered contributor</a>.</strong>
                                </div>
                                <div data-bind="if: noResults">
                                    No results found. Try a more specific search or <strong><a href="#"
                                    data-bind="click:gotoInvite">add <em>{{query}}</em> as an unregistered contributor</a>.</strong>
                                </div>
                            </div>
                        </div><!-- ./col-md -->

                        <div class="col-md-6">
                            <div>
                                <span class="modal-subheader">Adding</span>
                                <a data-bind="click:removeAll">Remove all</a>
                            </div>

                            <!-- TODO: Duplication here: Put this in a KO template -->
                            <table>
                                <tbody data-bind="foreach:{data:selection,
                                as: 'contributor',
                                afterRender:addTips}">
                                    <tr>
                                        <td style="padding-right: 10px;">
                                            <a
                                                    class="btn btn-default contrib-button"
                                                    data-bind="click:$root.remove"
                                                    rel="tooltip"
                                                    title="Remove contributor"
                                                >-</a>
                                        </td>
                                        <td>
                                            <img data-bind="attr:{src:contributor.gravatar}" />
                                        </td>
                                        <td><span data-bind="text: contributor.fullname"></span>
                                        <a href="#" class='text-muted'
                                                data-bind="
                                                    visible: !contributor.registered,
                                                    click: $root.goToPage.bind($data, 'invite')">(unregistered)
                                        </a></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                    </div>

                </div>
                <!-- Component selection page -->
                <div data-bind="if:page()=='which'">

                    <div>
                        Adding contributor(s)
                        <span data-bind="text:addingSummary()"></span>
                        to component
                        <span data-bind="text:title"></span>.
                    </div>

                    <hr />

                    <div style="margin-bottom:10px;">
                        Would you like to add these contributor(s) to any children of
                        the current component?
                    </div>

                    <div class="row">

                        <div class="col-md-6">
                            <input type="checkbox" checked disabled />
                            <span data-bind="text:title"></span> (current component)
                            <div data-bind="foreach:nodes">
                                <div data-bind="style:{'margin-left':margin}">
                                    <input type="checkbox" data-bind="checked:$parent.nodesToChange, value:id" />
                                    <span data-bind="text:title"></span>
                                </div>
                            </div>
                        </div>

                        <div class="col-md-6">
                            <div>
                                <a data-bind="click:selectNodes, css:{disabled:cantSelectNodes()}">Select all</a>
                            </div>
                            <div>
                                <a data-bind="click:deselectNodes, css:{disabled:cantDeselectNodes()}">De-select all</a>
                            </div>
                        </div>

                    </div>

                </div><!-- end component selection page -->

                <!-- Invite user page -->
                <div data-bind='if:page() === "invite"'>
                    <form class='form'>
                        <div class="form-group">
                            <label for="inviteUserName">Full Name</label>
                            <input type="text" class='form-control' id="inviteName"
                                placeholder="Full name" data-bind='value: inviteName, valueUpdate: "input"'/>
                        </div>
                        <div class="form-group">
                            <label for="inviteUserEmail">Email</label>
                            <input type="email" class='form-control' id="inviteUserEmail"
                                    placeholder="Email" data-bind='value: inviteEmail' autofocus/>
                        </div>
                         <div class="help-block">
                            <p>We will notify the user that they have been added to your project.</p>
                            <p class='text-danger' data-bind='text: inviteError'></p>
                        </div>
                    </form>
                </div><!-- end invite user page -->

            </div><!-- end modal-body -->

            <div class="modal-footer">

                <a href="#" class="btn btn-default" data-bind="click: clear" data-dismiss="modal">Cancel</a>

                <span data-bind="if: page() === 'invite'">
                    <button class="btn btn-primary" data-bind='click:selectWhom'>Back</button>
                    <button class='btn btn-success'
                         data-bind='click: postInvite'
                                    type="submit">Add</button>
                </span>

                <span data-bind="if:selection().length && page() == 'whom'">
                    <a class="btn btn-success" data-bind="visible:nodes().length==0, click:submit">Submit</a>
                    <a class="btn btn-primary" data-bind="visible:nodes().length, click:selectWhich">Next</a>
                </span>

                <span data-bind="if: page() == 'which'">
                    <a class="btn btn-primary" data-bind="click:selectWhom">Back</a>
                    <a class="btn btn-success" data-bind="click:submit">Submit</a>
                </span>

            </div><!-- end modal-footer -->
        </div><!-- end modal-content -->
    </div><!-- end modal-dialog -->
</div><!-- end modal -->