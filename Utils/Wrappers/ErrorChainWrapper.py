# coding=utf-8
from smartcard.sw.ErrorCheckingChain import ErrorCheckingChain
from smartcard.sw.ISO7816_4ErrorChecker import ISO7816_4ErrorChecker
from smartcard.sw.ISO7816_8ErrorChecker import ISO7816_8ErrorChecker
from smartcard.sw.ISO7816_9ErrorChecker import ISO7816_9ErrorChecker

ErrorChainWrapper = []
ErrorChainWrapper = [ErrorCheckingChain(ErrorChainWrapper, ISO7816_9ErrorChecker())]
ErrorChainWrapper = [ErrorCheckingChain(ErrorChainWrapper, ISO7816_8ErrorChecker())]
ErrorChainWrapper = [ErrorCheckingChain(ErrorChainWrapper, ISO7816_4ErrorChecker())]
