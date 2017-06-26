from burp import IBurpExtender, IContextMenuFactory, IContextMenuInvocation

from javax.swing import JMenuItem, JMenu, JFrame

from functools import partial
from script_editor import ScriptEditor, HttpMessage

class ScriptExporter(object):
    def __init__(self, callbacks, requests):
        pass

class BurpExtender(IBurpExtender, IContextMenuFactory):

    def registerExtenderCallbacks(self, callbacks):
        callbacks.setExtensionName("Export as a script")
        callbacks.registerContextMenuFactory(self)
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()

    def createMenuItems(self, invocation):
        if invocation.getInvocationContext() == IContextMenuInvocation.CONTEXT_PROXY_HISTORY:
            item = JMenuItem(
                "Export as script",
                actionPerformed=partial(
                    self.export,
                    invocation.getSelectedMessages()
                )
            )
            return [item]

    def export(self, messages, event):
        chain = []
        for msg in messages:
            req = msg.getRequest()
            resp = msg.getResponse()
            req_info = self._helpers.analyzeRequest(msg)
            resp_info = self._helpers.analyzeResponse(resp)
            
            chain.append(HttpMessage(
                    http_service=msg.getHttpService(),
                    req_data=req,
                    req_info=req_info,
                    resp_data=resp,
                    resp_info=resp_info,
                )
            )
        ScriptEditor(chain)
